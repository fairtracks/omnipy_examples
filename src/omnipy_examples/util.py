from omnipy import HttpUrlDataset, Model, TaskTemplate, HttpUrlModel, JsonListOfDictsDataset

@TaskTemplate()
def get_github_repo_urls(owner: str, repo: str, branch: str, path: str,
                         file_suffix: str|None = None) -> HttpUrlDataset:

    url_pre = HttpUrlModel('https://raw.githubusercontent.com')
    url_pre.path // owner // repo // branch // path

    if file_suffix:
        api_url = HttpUrlModel('https://api.github.com')
        api_url.path // 'repos' // owner // repo // 'contents' // path
        api_url['ref'] = branch

        json_data = JsonListOfDictsDataset()
        json_data.load(api_url)
        names = Model[list[str]]([f['name'] for f in json_data[0] if f['name'].endswith(file_suffix)])
        return HttpUrlDataset({name: f'{url_pre}/{name}' for name in names})
    else:
        name = url_pre.path.name
        return HttpUrlDataset({name: f'{url_pre}/{name}'})
