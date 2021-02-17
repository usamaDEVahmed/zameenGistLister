from django.shortcuts import render, redirect
from gist_lister.forms import UserForm
import requests
from urllib.parse import urljoin
from gist_lister.gist_file import Gist

# NOTES
# 1) The AVATAR associated to all the users are made accessible as anchor tags
# 2) The AVATAR can be accessed when the list of gists are generated or
#    a specific gist is opened in case of accessing usernames & avatars of
#    the users who forked from the gist
# 3) To actually access an avatar just click the username(nested as anchor tags)
# 4) The TAGS associated to a gist can be seen when a specific gist is opened
#    same goes for the avatars and username of the users.

# The gists are listed according to their specific ID

def get_url(username):
    """
    :param username: the GitHub username, whose all the public gists are to be obtained
    :return: finalized URL to which the HTTP request can be made to get all of the gists of a particular user
    """
    raw_url = 'https://api.github.com/users/' + username + '/'
    final_url = urljoin(raw_url, 'gists')
    return final_url


def get_gists(url):
    """
    :param url: The URL to which the HTTP GET request is made to get all of the gists
    :return: A list of all of the public gists
    """
    gists = [] # the list that will contain all of the public gists
    response = requests.get(url, auth=('usamaDEVahmed', '338aea5d31987491308025f4017c574ed5bab138'))
    # extracting each gist form the GET request
    for each in response.json():
        # extracting only public gists
        if each['public']:
            # appending gists list with a Gist class's object that is created in gist_file.py
            gists.append(Gist(url=each['url'],
                              forks_url=each['forks_url'],
                              commits_url=each['commits_url'],
                              id=each['id'],
                              git_pull_url=each['git_pull_url'],
                              git_push_url=each['git_push_url'],
                              files=each['files'],
                              owner=each['owner']))

            # separately initializing files as a prototype of Gist class' object
            # Because it has to contain specific information w.r.t each file
            # i.e.
            # 1) the file name
            # 2) the language of the content of the file
            # 3) the tags of the file e.g. python, java etc
            # 4) the URL of the actual content of the file
            # 5) the actual content of the file. NOTE: The content of the gist file is downloaded only when the
            #    particular gist is accessed to reduce system overhead
            gists[-1].set_gist_files()

            # another prototype of the Gist class that will contain information about the last 3 users
            # who forked the gist. It will contain:
            # 1) the username
            # 2) the avatar associated to that usee
            gists[-1].set_last_three_forkers()

    # finally, returning the gist
    return gists


# The very first view that will be displayed to the end-user
def index(request):
    """
    :param request: HTTP request
    :return: the HTML document containing the from where user will enter username to access gists
    """

    # if the request is HTTP POST that means user has entered the username and searched for the gists
    if request.method == 'POST':
        username = None
        form = UserForm(request.POST)
        if form.is_valid():
            # getting the username
            username = form.cleaned_data['username']
            # creating a session for the username to use it across multiple views
            request.session['username'] = username

            # redirecting the HTML document which will list all of the gists of that searched user
            return redirect('gist_lister:list_gists_view')
    else:
        # if the request is HTTP GET
        form = UserForm()
        # generating the form where user will enter username to search for the gists
        return render(request, 'gist_lister/index.html', context={'form': form})


# that view that will list all of the gists of the searched user
def list_gists_view(request):
    """
    :param request: HTTP request
    :return: redirect to the clicked gist to see the files associated with that gist
    """
    if request.method == 'GET':
        # NOTE: This is where session variable for username is used and all of the gists are downloaded
        gists = get_gists(get_url(request.session['username']))

        # creating separate list to contain the unique ids associated to every gist for further use
        gists_ids = []
        for each in gists:
            gists_ids.append(each.id)

        # generating the HTML document that will display the list of all the gists
        response = render(request, 'gist_lister/list_gists.html', {'gists': gists})
        # creating a COOKIE for the ids of gists to use them across multiple views
        response.set_cookie('gists_ids', gists_ids)
        return response

    # if the HTTP method is POST that means the user has clicked on a specific to see its contents
    elif request.method == 'POST':
        # getting the ids of the gists
        ids = request.COOKIES.get('gists_ids').split(',')
        gists_ids = []
        # filtering all of the ids because of data transformation due to COOKIE creation i.e. gists_ids was a list
        # and COOKIE made all the list a string
        i = 0
        while i < len(ids):
            if i == 0:
                gists_ids.append(ids[i][1:].strip().strip('"')[1:-1])
            elif i == len(ids)-1:
                gists_ids.append(ids[i][:-1].strip().strip('"')[1:-1])
            else:
                gists_ids.append(ids[i].strip().strip('"')[1:-1])
            i += 1

        # Now getting the id of the gist that was clicked by the user to filter out its files from all of the gists
        clicked_button_id = None
        for each in gists_ids:
            if request.POST.get(each):
                clicked_button_id = each
                break
        request.session['gist_id'] = clicked_button_id

        # redirecting to the final page where file's content will be displayed
        return redirect('gist_lister:file_content_view')


# the final view of the project which will display to contents of the files associated tot a gist
def file_content_view(request):
    """
    :param request: HTTP request
    :return: the HTML document that will display the specific gist's contents
    """
    context = {}
    gist_id = request.session['gist_id']

    # filtering out the selected gist
    gists = get_gists(get_url(request.session['username']))
    required_gist = None
    for each in gists:
        if each.id == gist_id:
            required_gist = each

    # downloading the contents of all the existing files associated to that gist
    for each in required_gist.gist_files:
        each.file_content = requests.get(each.file_content_url)

    # creating a dictionary to send the necessary information to the HTML document
    # to populate the document with the gist's contents
    context['files'] = required_gist.gist_files
    context['forker'] = required_gist.last_three_users

    return render(request, 'gist_lister/file_content.html', context)
