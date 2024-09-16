import httpx
from omnipy import JsonModel, Model, StrDataset, TaskTemplate


@TaskTemplate
def get_github_repo_urls(owner: str, repo: str, path: str, file_suffix: str,
                         branch: str) -> StrDataset:
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}'
    url_pre = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}'

    json_data = JsonModel(httpx.get(api_url).raise_for_status().json())
    names = Model[list[str]]([f['name'] for f in json_data if f['name'].endswith(file_suffix)])
    return StrDataset({name: f'{url_pre}/{name}' for name in names})
