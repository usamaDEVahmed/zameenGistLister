import pandas as pd
import requests


# A helper class that is used to store the data related to a user's gist in a orderly manner
class Gist():
    def __init__(self, url, forks_url, commits_url, id, git_pull_url, git_push_url, files, owner):
        self.url = url # the url of the gist
        self.forks_url = forks_url # the url related to the forks to the gist
        self.commits_url = commits_url # the url to the all the commits made to the gist
        self.id = id    # specific ID of the gist
        self.git_pull_url = git_pull_url
        self.git_push_url = git_push_url
        self.files = files  # files associated to the gist
        self.owner = owner['login']     # the owner name of that gist
        self.avatar = owner['avatar_url']   # the avatar associated to the owner
        self.last_three_users = []  # the most recent last 3 users who forked from the gist
        self.gist_files = []    # the adjusted gist files containing data specifically to the files

    # storing the gist files
    def set_gist_files(self):
        filenames = list(self.files.keys())
        for each in filenames:
            self.gist_files.append(GistFile(filename=each,
                                            file_language=str(self.files[each]['language']),
                                            file_tag=str(self.files[each]['language']),
                                            file_content_url=self.files[each]['raw_url']))

    # storing the last 3 users who forked from the gist
    def set_last_three_forkers(self):

        response = requests.get(self.forks_url, auth=('usamaDEVahmed', '338aea5d31987491308025f4017c574ed5bab138'))
        if response.json():
            # storing data in the dataframe to organize it
            dataframe = pd.read_json(response.json())

            # sorting out the dataframe according to commit dates to get the most recent forks
            dataframe['updated'] = None
            for i, j in dataframe.iterrows():
                sub_dataframe = pd.read_json(j['commits_url'])
                dataframe['updated'].loc[i] = sub_dataframe['committed_at'][0]

            most_recent_three_forks = dataframe.sort_values(by='updated',
                                                            ascending=False).head(3)

            # actually storing the 3 most recent forks
            for each in most_recent_three_forks:
                self.last_three_users.append((each['owner']['login'], each['owner']['avatar_url']))

# class whose objects are used to specifically store data to the gist's files
class GistFile():
    def __init__(self, filename, file_language, file_tag, file_content_url):
        self.filename = filename
        self.file_language = file_language # language used in the file
        self.file_tag = file_tag    # the tags related to the file
        self.file_content_url = file_content_url    # the URL of the content of the file
        self.file_content = None    # the original content of the file.
        # NOTE: The content of the gist file is downloaded only when the
