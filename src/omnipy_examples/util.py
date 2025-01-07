import httpx
from omnipy import HttpUrlDataset, JsonModel, Model, TaskTemplate


@TaskTemplate()
def get_github_repo_urls(owner: str, repo: str, branch: str, path: str,
                         file_suffix: str) -> HttpUrlDataset:
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}'
    url_pre = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}'

    json_data = JsonModel(httpx.get(api_url).raise_for_status().json())
    names = Model[list[str]]([f['name'] for f in json_data if f['name'].endswith(file_suffix)])
    return HttpUrlDataset({name: f'{url_pre}/{name}' for name in names})
