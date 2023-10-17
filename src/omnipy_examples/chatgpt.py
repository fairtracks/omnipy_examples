import asyncio
from asyncio import Future
from pathlib import Path
import random
import textwrap
import time

import github3
import httpx
from omnipy import runtime
from omnipy.compute.flow import FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from omnipy_examples.chatgpt_words import (literary_styles,
                                           surrealistic_adjectives,
                                           surrealistic_nouns)
from pydantic.main import BaseModel
from reader import Feed, make_reader

biorxiv_feed_url = 'https://connect.biorxiv.org/biorxiv_xml.php?subject=all'
chatgpt_secret_key = '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'

# TODO: Implement omnified way of managing API keys and other secrets

# Models


class PaperInfo(BaseModel):
    id: str = ''
    title: str = ''
    abstract: str = ''


class PaperInfoWithPrompt(PaperInfo):
    prompt: str = ''


class PaperInfoWithPromptAndInterpretation(PaperInfoWithPrompt):
    interpretation: str = ''


class PaperInfoDataset(Dataset[Model[PaperInfo]]):
    ...


class PaperInfoWithPromptDataset(Dataset[Model[PaperInfoWithPrompt]]):
    ...


class PaperInfoWithPromptAndInterpretationDataset(
        Dataset[Model[PaperInfoWithPromptAndInterpretation]]):
    ...


@TaskTemplate()
def get_latest_entries(feed_url: str, max_entries_per_run: int) -> PaperInfoDataset:
    dataset = PaperInfoDataset()

    db_path = Path(runtime.config.root_log.file_log_dir_path).parent.joinpath('db.sqlite')
    reader = make_reader(str(db_path))
    reader.add_feed(feed_url, exist_ok=True)
    reader.update_feeds()

    for i, entry in enumerate(reader.get_entries(read=False)):
        if i >= max_entries_per_run:
            break

        reader.mark_entry_as_read(entry)

        title = entry.title.replace('/', '-')
        dataset[title] = PaperInfo(
            id=entry.id,
            title=title,
            abstract=entry.summary,
        )

    return dataset


def pick_a_word(word_list: list[str]):
    return random.sample(word_list, 1)[0].lower()


@TaskTemplate(iterate_over_data_files=True)
def generate_prompt(
    paper: PaperInfo,
    genres: list[str],
    adjectives: list[str],
    nouns: list[str],
) -> PaperInfoWithPrompt:
    prompt = f'Here follows the abstract of a scientific paper recently published at' \
             f'bioRxiv ({paper.id}):\n\n{paper.abstract}\n\n' \
             f'Based on the above abstract, can you write a text in the literary ' \
             f'style of {pick_a_word(genres)}, where the text has stylistic ' \
             f'qualities best described as {pick_a_word(adjectives)} and {pick_a_word(adjectives)}, ' \
             f'and which also somehow includes a {pick_a_word(nouns)} and a {pick_a_word(nouns)} ' \
             f'multiple times in the discussion?'
    return PaperInfoWithPrompt(
        id=paper.id,
        title=paper.title,
        abstract=paper.abstract,
        prompt=prompt,
    )


@LinearFlowTemplate(
    get_latest_entries.refine(fixed_params=dict(
        feed_url=biorxiv_feed_url,
        max_entries_per_run=5,
    )),
    generate_prompt.refine(
        fixed_params=dict(
            genres=literary_styles,
            adjectives=surrealistic_adjectives,
            nouns=surrealistic_nouns,
        )),
)
async def get_biorxiv_entries_and_generate_prompts() -> PaperInfoWithPromptDataset:
    ...


# get_biorxiv_entries_and_generate_prompts.run()

# Possible simplification?
#
# @TaskTemplate(async_iterate_over_data_files=True, async_run_until_complete=True, async_batch_size=1)
# async def generate_responses(paper: PaperInfo) -> Future:
#     API_KEY = chatgpt_secret_key
#     API_ENDPOINT = 'https://api.openai.com/v1/completions'
#     await async_http_post(endpoint=API_ENDPOINT, headers={'Authorization': f'Bearer {API_KEY}'})


@TaskTemplate()
async def generate_response(paper: PaperInfo) -> Future:
    API_KEY = chatgpt_secret_key
    API_ENDPOINT = 'https://api.openai.com/v1/completions'

    async with httpx.AsyncClient() as client:
        # with httpx.Client() as client:
        response = await client.post(
            # response = client.post(
            API_ENDPOINT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}',
            },
            json={
                'model': 'text-davinci-003',
                'prompt': paper.prompt,
                'max_tokens': 400,
                'temperature': 0.9,
            },
            timeout=200)
        # return response.json()['choices'][0]['text']
        return response.json()


# Possible simplification of first half of generate_responses_for_all_prompts?
#    responses = generate_responses(papers)


@FuncFlowTemplate
def generate_responses_for_all_prompts(papers: PaperInfoWithPromptDataset):
    loop = asyncio.new_event_loop()
    tasks = [generate_response(paper) for paper in papers.values()]
    # for paper in papers.values():
    #     tasks.append(generate_response(paper))
    #     time.sleep(1)
    responses = loop.run_until_complete(asyncio.wait(tasks))[0] if tasks else []
    response_dict = {key: response.result() for key, response in zip(papers.keys(), responses)}

    dataset = PaperInfoWithPromptAndInterpretationDataset()
    for key, paper in papers.items():
        dataset[key] = PaperInfoWithPromptAndInterpretation(
            id=paper.id,
            title=paper.title,
            abstract=paper.abstract,
            prompt=paper.prompt,
            interpretation=response_dict[key]['choices'][0]['text'],
        )
    return dataset


@TaskTemplate(iterate_over_data_files=True)
def commit_info_to_github_repo(paper: PaperInfoWithPromptAndInterpretation,
                               branch: str = 'main') -> PaperInfoWithPromptAndInterpretation:
    # Authenticate with a personal access token
    gh = github3.login(
        token=
        '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'
    )

    # Get the repository by owner and name
    repo = gh.repository('fairtracks', 'biorxiv_chatgpt')

    filename = paper.id.split('/')[-1].split('?')[0]
    contents = paper.prompt + '\n\nInterpretation of "text-davinci-003":\n' + paper.interpretation
    contents = textwrap.fill(contents, 80, replace_whitespace=False)
    # Create a new file in the repository
    repo.create_file(
        path=f'papers/{filename}.txt',
        message=f'Adding "{paper.title}"',
        content=contents.encode('utf8'),
        branch='wp3_finse_test')

    # Commit the changes with a commit message
    # last_commit = list(repo.commits())[-1]

    # Push the changes to the remote repository
    # last_commit.push()

    return paper


@LinearFlowTemplate(
    get_biorxiv_entries_and_generate_prompts,
    generate_responses_for_all_prompts,
)
def get_chatgpt_interpretation_of_biorxiv_entries() -> PaperInfoWithPromptAndInterpretationDataset:
    ...


@LinearFlowTemplate(
    get_chatgpt_interpretation_of_biorxiv_entries,
    commit_info_to_github_repo,
)
def get_chatgpt_interpretation_of_biorxiv_entries_and_commit(
) -> PaperInfoWithPromptAndInterpretationDataset:
    ...


@FuncFlowTemplate()
def get_chatgpt_interpretation_of_biorxiv_entries_and_commit_loop(
) -> PaperInfoWithPromptAndInterpretationDataset:
    while True:
        papers = get_chatgpt_interpretation_of_biorxiv_entries_and_commit()
        if len(papers) == 0:
            break
        time.sleep(60)


def main():
    # generate_response.run(q)
    # asyncio.run(generate_response.run(q))
    get_chatgpt_interpretation_of_biorxiv_entries_and_commit_loop.run()


# await print(generate_response('What is ChatGPT?'))

if __name__ == '__main__':
    main()
    # import asyncio
    # asyncio.run(main())

# get_latest_entries.run(biorxiv_feed_url)
