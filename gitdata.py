import os


class AllRepositories:
    analysis_number = 0

    def __init__(self, repos, output_filepath=None, time_window_days=None):
        self.repos = repos
        self.start_date = None
        self.end_date = None
        self.output_filepath = output_filepath
        self.time_window_days = time_window_days

        AllRepositories.analysis_number += 1

        if self.count_total_pull_requests() > 0:
            self.fill_analysis_dates()
            self.fill_filepath()
            self.display_pulls_per_day()
            self.display_open_vs_closed_per_day()
            self.display_users_per_repository()
            print('Figures have been saved to: ' + os.path.abspath(self.output_filepath))
        else:
            print('No pull requests found in list of repos')

    def count_total_pull_requests(self):
        count = 0
        if len(self.repos) > 0:
            for repo in self.repos:
                count += len(repo.pull_requests)
        return count

    def fill_filepath(self):
        import os

        if self.output_filepath is not None:
            if not os.path.exists(self.output_filepath):
                os.mkdir(self.output_filepath)

        if self.output_filepath is None:
            outdir = f"all_repos_analysis_{AllRepositories.analysis_number}/"
        else:
            outdir = self.output_filepath + '/' + f"all_repos_analysis_{AllRepositories.analysis_number}/"

        if not os.path.exists(outdir):
            os.mkdir(outdir)

        self.output_filepath = outdir

    def fill_analysis_dates(self):
        from datetime import date, datetime, timedelta
        if self.time_window_days is not None:
            # use datetime package to create start and end dates for the last n days
            self.end_date = date.today()
            self.start_date = self.end_date - timedelta(days=self.time_window_days)
        else:
            dates = list()
            for repo in self.repos:
                for pull in repo.pull_requests:
                    dates.append(pull.created_at)
            dates.sort()
            self.start_date = datetime.strptime(dates[0], '%Y-%m-%dT%H:%M:%SZ').date()
            self.end_date = datetime.strptime(dates[-1], '%Y-%m-%dT%H:%M:%SZ').date()

    def display_pulls_per_day(self):
        import pandas as pd
        dfs = list()
        for repo in self.repos:
            temp_df = repo.pull_requests_to_pandas()
            dfs.append(temp_df)

        df = pd.concat(dfs)

        # this will remove the hours, minutes and seconds data from the created_at field and leave us with just the date
        df['created_at'] = pd.to_datetime(df['created_at'].str.split('T').str[0])

        try:
            # create dataframe of last 60 days
            analysis_days = pd.DataFrame({'date': pd.date_range(start=self.start_date, end=self.end_date, freq='1d')})
            # create a tally column that queries our pull requests to find the number of requests opened for each day
            analysis_days['tally'] = analysis_days['date'].apply(lambda x: len(df.query("created_at == @x")))
            # plot the tallies per day
            ax = analysis_days.plot.line(x='date', y='tally')
            # display and save fig
            # print(ax)
            ax.figure.savefig(self.output_filepath + 'pulls_per_day.png', bbox_inches='tight')


        except Exception as e:
            # this is just for troubleshooting our code and testing, we shouldn't need it once we have this perfected
            print('something is wrong with the data, here is the error: ')
            print(e)

        return None

    def display_open_vs_closed_per_day(self):
        import pandas as pd
        dfs = list()

        for repo in self.repos:
            temp_df = repo.pull_requests_to_pandas()
            dfs.append(temp_df)

        df = pd.concat(dfs)

        # this will remove the hours, minutes and seconds data from the created_at and closed_at fields so we only have the date
        df['created_at'] = pd.to_datetime(df['created_at'].str.split('T').str[0])
        df['closed_at'] = pd.to_datetime(df['closed_at'].str.split('T').str[0])

        try:
            # create dataframe of last 60 days
            analysis_days = pd.DataFrame({'date': pd.date_range(start=self.start_date, end=self.end_date, freq='1d')})
            # create an open and close tally column that queries our pull requests to find the number of requests opened and closed for each day
            analysis_days['open_tally'] = analysis_days['date'].apply(lambda x: len(df.query("created_at == @x")))
            analysis_days['close_tally'] = analysis_days['date'].apply(lambda x: len(df.query("closed_at == @x")))
            # plot open vs close per day, this will automatically color between open and close tallies
            ax = analysis_days.plot.line(x='date')
            # display and save fig
            # print(ax)

            ax.figure.savefig(self.output_filepath + 'open_vs_closed_per_day.png', bbox_inches='tight')


        except Exception as e:
            # this is just for troubleshooting our code and testing, we shouldn't need it once we have this perfected
            print('something is wrong with the data, here is the error: ')
            print(e)

        return None

    def display_users_per_repository(self):
        import pandas as pd
        # initialize list of dicts
        repo_users = list()
        # iterate across all repos
        for repo in self.repos:
            # initialize dictionary
            temp_dict = dict()
            temp_dict['repo_name'] = repo.repo_name
            temp_dict['users'] = len(repo.users)
            repo_users.append(temp_dict)

        # create dataframe from list of dicts, display, and save fig
        df = pd.DataFrame(repo_users)
        ax = df.plot.bar(x='repo_name', y='users', rot=0)
        # print(ax)

        ax.figure.savefig(self.output_filepath + 'users_per_repository.png', bbox_inches='tight')

        return None


# Placeholder definition for the GitHubLicense class
class GitHubLicense:
    def __init__(self, name, spdx_id):
        self.name = name
        self.spdx_id = spdx_id

    def __str__(self):
        return f"{self.name} ({self.spdx_id})"


class Repository:
    def __init__(self, owner_name, repo_name, time_window_days=365, verbose=True, token=None, output_filepath=None):
        # Assign properties
        self.owner_name = owner_name
        self.repo_name = repo_name
        self.time_window_days = time_window_days
        self.verbose = verbose
        self.__token = token
        self.output_filepath = output_filepath

        # Initialize empty variables for pull request data and contributing user data
        self.pull_requests = tuple()
        self.users = tuple()

        # Automatically run function to get pull requests and users
        self.get_pulls()
        self.get_users()

        self.fill_filepath()

    def fill_filepath(self):
        import os

        if self.output_filepath is not None:
            if not os.path.exists(self.output_filepath):
                os.mkdir(self.output_filepath)

        if self.output_filepath is None:
            outdir = f"repo_summary_{self.repo_name}/"
        else:
            outdir = self.output_filepath + '/' + f"repo_summary_{self.repo_name}/"

        if not os.path.exists(outdir):
            os.mkdir(outdir)

        self.output_filepath = outdir

    def get_pulls_as_json(self):
        # GitHub API endpoint for pull requests
        url = f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/pulls"

        pull_requests_json = get_github_api_request(url=url, params={'state': 'all', 'per_page': '100'},
                                                    time_window_days=self.time_window_days, token=self.__token)

        return pull_requests_json

    def get_pulls(self):
        # Get pull requests from github in json format
        pulls_json = self.get_pulls_as_json()
        if self.verbose:
            print(f'Found {len(pulls_json)} pull requests in this time window. Downloading detailed data...')

        # Temporarily create an empty list
        pull_requests_list = list()

        # Convert each pull request in the json to a PullRequest object and add it
        # to the list of pull requests stored in this Repository object
        finished = 0
        total = len(pulls_json)
        tics = list(range(0, 100, 10))
        for json_record in pulls_json:
            if self.verbose:
                progress = int(((
                                            finished * .7) / total) * 100)  # Testing showed that downloading pull request data takes ~70% of time, downloading user data takes ~30% of the total time
                if progress >= tics[0]:
                    progress = tics.pop(0)
                    print('[' + '#' * (progress // 5) + '-' * ((100 - progress) // 5) + '] ' + str(progress) + '%')

            pull_request_instance = PullRequest(token=self.__token)
            pull_request_instance.fill_from_json(json_record)
            pull_requests_list.append(pull_request_instance)
            finished += 1

        # Convert list to tuple so it's safer from accidental changes
        self.pull_requests = tuple(pull_requests_list)

    def pull_requests_to_json(self):
        output_list = list()
        for pull_request in self.pull_requests:
            output_list.append(pull_request.to_dict())

        return output_list

    def pull_requests_to_pandas(self):
        import pandas as pd
        return pd.DataFrame(self.pull_requests_to_json())

    def get_users_as_json(self, username):
        # GitHub API endpoint for pull requests
        url = f"https://api.github.com/users/{username}"

        users_json = get_github_api_request(url=url, convert_json=True, token=self.__token)

        return users_json

    def get_users(self, token=None):
        # Temporarily create an empty list
        user_list = list()
        user_names = list()

        # iterate across pull requests
        finished = 0
        start = len(self.pull_requests) * .7
        total = len(self.pull_requests)
        tics = list(range(70, 120, 10))
        for pull in self.pull_requests:
            if self.verbose:
                progress = int(((start + finished * .3) / total) * 100)
                if progress >= tics[0]:
                    progress = tics.pop(0)
                    print('[' + '#' * (progress // 5) + '-' * ((100 - progress) // 5) + '] ' + str(progress) + '%')

            # check if name in user list

            if pull.user not in user_names:
                # Get pull requests from github in json format
                user_json = self.get_users_as_json(pull.user)

                # Convert each user to a user object and add it
                # to the list of users stored in this Repository object
                user_instance = User(name=pull.user, token=self.__token)
                user_instance.fill_from_json(user_json)
                user_list.append(user_instance)
                user_names.append(pull.user)

            else:
                # otherwise add another contribution tally to the user
                existing_user_index = user_names.index(pull.user)
                user_list[existing_user_index].contributions += 1

            finished += 1

        # Convert list to tuple so it's safer from accidental changes
        self.users = tuple(user_list)

        if self.verbose:
            if 100 in tics:
                progress = 100
                print('[' + '#' * (progress // 5) + '-' * ((100 - progress) // 5) + '] ' + str(progress) + '%')

    def users_to_json(self):
        output_list = list()
        for user in self.users:
            output_list.append(user.to_dict())

        return output_list

    def users_to_pandas(self):
        import pandas as pd
        return pd.DataFrame(self.users_to_json())

    def total_user(self):
        total_users_set = set()
        for pull in self.pull_requests:
            total_users_set.add(pull.user)
        total_users = len(total_users_set)
        return total_users

    def user_correlations(self):
        import pandas as pd
        if len(self.users) > 0:
            # convert user data to a dataframe
            df = self.users_to_pandas()

            # grab the four metrics we need to run pairwise correlation
            corr_subset = df[['followers', 'following', 'public_repos', 'contributions']]

            # calculate pairwise correlations between fields
            correlations = corr_subset.corr()
        else:
            print("No users were found in this repository's pull requests")
            correlations = None

        # display results
        return correlations

    def total_pulls_closed(self):
        pull_closed_total = 0
        for pull in self.pull_requests:
            if pull.state == 'closed':
                pull_closed_total += 1
        return pull_closed_total

    def total_pulls_open(self):
        pull_open_total = 0
        for pull in self.pull_requests:
            if pull.state == 'open':
                pull_open_total += 1
        return pull_open_total

    def oldest(self):
        dates = []
        for pull in self.pull_requests:
            # if pull.state == 'open':
            dates.append(pull.created_at)
        dates.sort()
        if len(dates) > 0:
            oldest_date = dates[0]
        else:
            oldest_date = 'NA'
        return oldest_date

    def __repr__(self):
        return f'Repository(owner_name: {self.owner_name}, repo_name: {self.repo_name}, n_pull_requests: {len(self.pull_requests)})'

    def to_dict(self):
        return {'owner_name': self.owner_name, 'repo_name': self.repo_name, 'n_pull_requests': len(self.pull_requests),
                'n_users': len(self.users)}

    def to_csv_header(self):
        import csv
        import io
        csv_output = io.StringIO()
        # Create a CSV writer
        csv_writer = csv.writer(csv_output, dialect='excel')

        # Write a single row that could be the headers
        csv_writer.writerow(['owner_name', 'repo_name', 'n_pull_requests', 'n_users'])

        # Get the CSV-formatted string from the virtual file
        csv_string = csv_output.getvalue().encode('ascii', 'ignore').decode('ascii')
        csv_output.close()

        return csv_string

    def to_csv_record(self):
        import csv
        import io
        csv_output = io.StringIO()
        # Create a CSV writer
        csv_writer = csv.writer(csv_output, dialect='excel')

        # Write a single row that could be the headers
        csv_writer.writerow([self.owner_name, self.repo_name, len(self.pull_requests), len(self.users)])

        # Get the CSV-formatted string from the virtual file
        csv_string = csv_output.getvalue().encode('ascii', 'ignore').decode('ascii')

        csv_output.close()

        return csv_string

    def save_to_csv(self):
        # Save to repositories.csv
        save_as_csv('repositories.csv', self)

        # Save to repos/owner-repo.csv
        repo_csv_path = os.path.join('repos', f'{self.owner_name}-{self.repo_name}.csv')
        save_as_csv(repo_csv_path, self)

    def box_closed_open_commit(self):
        import pandas as pd
        if len(self.pull_requests) > 0:
            temp_dict = {'commit': [], 'state': []}
            for pull in self.pull_requests:
                temp_dict['state'].append(pull.state)
                temp_dict['commit'].append(pull.num_commits)
            df = pd.DataFrame(temp_dict).dropna()
            ax = df.plot.box(by="state", return_type='axes', showfliers=False)
            ax['commit'].figure.savefig(self.output_filepath + 'box_closed_open_commit.png', bbox_inches='tight')

        else:
            print('No pull requests found')

    def box_addition_deletion(self):
        import pandas as pd
        if len(self.pull_requests) > 0:
            temp_dict = {'addition': [], 'deletion': [], 'state': []}
            for pull in self.pull_requests:
                temp_dict['state'].append(pull.state)
                temp_dict['addition'].append(pull.num_additions)
                temp_dict['deletion'].append(pull.num_deletions)
            df = pd.DataFrame(temp_dict).dropna()
            ax = df.plot.box(by="state", return_type='axes', showfliers=False)
            ax['addition'].figure.savefig(self.output_filepath + 'box_addition_deletion.png', bbox_inches='tight')

        else:
            print('No pull requests found')

    def scatter_addition_deletion(self):
        import pandas as pd
        import matplotlib.pyplot as plt
        if len(self.pull_requests) > 0:
            temp_dict = {'addition': [], 'deletion': []}
            for pull in self.pull_requests:
                temp_dict['addition'].append(pull.num_additions)
                temp_dict['deletion'].append(pull.num_deletions)
            df = pd.DataFrame(temp_dict)
            # Remove data that is more than 3 standard deviations from the mean
            additions_extreme_threshold = df['addition'].mean() + df['addition'].std() * 3
            deletions_extreme_threshold = df['deletion'].mean() + df['deletion'].std() * 3
            df = df[df['addition'] <= additions_extreme_threshold]
            df = df[df['deletion'] <= deletions_extreme_threshold]
            df = df.dropna()
            scatterplot = df.plot.scatter(x='addition', y='deletion')
            scatterplot.figure.savefig(self.output_filepath + 'scatter_addition_deletion.png', bbox_inches='tight')

        else:
            print('No pull requests found')

    def pull_request_correlations(self):
        if len(self.pull_requests) > 0:
            # convert user data to a dataframe
            df = self.pull_requests_to_pandas()

            # grab the four pull request fields we need to run pairwise correlation
            corr_subset = df[['num_commits', 'num_additions', 'num_deletions', 'num_changed_files']]

            # calculate pairwise correlations between fields
            correlations = corr_subset.corr()
        else:
            print('No pull requests found')
            correlations = None

        return correlations

    def file_changes_per_user(self):
        if len(self.pull_requests) > 0:
            # convert user data to a dataframe
            df = self.pull_requests_to_pandas()

            # create a subset dataframe with the two fields we need
            subset = df[['user', 'num_changed_files']]
            # subset = subset.groupby(['user']).sum()

            # create a barplot with the
            correlations = subset.plot.box(by='user', showfliers=False, return_type='axes')
            correlations['num_changed_files'].figure.savefig(self.output_filepath + 'file_changes_per_user.png',
                                                             bbox_inches='tight')

        else:
            print('No pull requests found')


class PullRequest:
    def __init__(self, title: str = None, number: int = None, body: str = None, state: str = None,
                 created_at: str = None, closed_at: str = None,
                 user: str = None, commits: str = None, additions: str = None, deletions: str = None,
                 changed_files: str = None, token=None):
        self.title = title
        self.number = number
        self.body = body
        self.state = state
        self.created_at = created_at
        self.closed_at = closed_at
        self.user = user
        self.num_commits = commits
        self.num_additions = additions
        self.num_deletions = deletions
        self.num_changed_files = changed_files

        self.__token = token  # Store token for making API requests. DO NOT INCLUDE IN OUTPUTS.

    def fill_from_json(self, json):
        self.title = json['title']
        self.number = json['number']
        self.body = json['body']
        self.state = json['state']
        self.created_at = json['created_at']
        self.closed_at = json['closed_at']
        self.user = json['user']['login']
        self.url = json['url']  # Don't need to output
        self.commits_url = json['commits_url']  # Don't need to output
        self.diff_url = json['diff_url']  # Don't need to output

        self.get_diff_metrics()

    def to_dict(self):
        return {'title': self.title,
                'number': self.number,
                'body': self.body,
                'state': self.state,
                'created_at': self.created_at,
                'closed_at': self.closed_at,
                'user': self.user,
                'num_commits': self.num_commits,
                'num_additions': self.num_additions,
                'num_deletions': self.num_deletions,
                'num_changed_files': self.num_changed_files,
                }

    def get_diff_metrics(self):
        # Download diff data from API
        pull_json = get_github_api_request(self.url, token=self.__token)

        self.num_additions = pull_json['additions']
        self.num_deletions = pull_json['deletions']
        self.num_changed_files = pull_json['changed_files']
        self.num_commits = pull_json['commits']

    def __str__(self):
        return f'Pull Request #{self.number}: {self.title}'

    def __repr__(self):
        return f'PullRequest(number:{self.number}, title:{self.title})'

    def to_csv_header(self):
        import csv
        import io
        csv_output = io.StringIO()
        # Create a CSV writer
        csv_writer = csv.writer(csv_output, dialect='excel')

        # Write a single row that could be the headers
        csv_writer.writerow(
            ['title', 'number', 'body', 'state', 'created_at', 'closed_at', 'user', 'num_commits', 'num_additions',
             'num_deletions', 'num_changed_files'])

        # Get the CSV-formatted string from the virtual file
        csv_string = csv_output.getvalue().encode('ascii', 'ignore').decode('ascii')

        csv_output.close()

        return csv_string

    def to_csv_record(self):
        import csv
        import io
        csv_output = io.StringIO()
        # Create a CSV writer
        csv_writer = csv.writer(csv_output, dialect='excel')

        # Write a single row that could be the headers
        csv_writer.writerow([self.title, self.number, self.body, self.state, self.created_at, self.closed_at, self.user,
                             self.num_commits, self.num_additions, self.num_deletions, self.num_changed_files, ])

        # Get the CSV-formatted string from the virtual file
        csv_string = csv_output.getvalue().encode('ascii', 'ignore').decode('ascii')

        csv_output.close()

        return csv_string

    def save_to_csv(self, owner_name, repo_name):
        # Save to repos/owner-repo.csv
        repo_csv_path = os.path.join('repos', f'{owner_name}-{repo_name}.csv')
        save_as_csv(repo_csv_path, self)


class User:
    def __init__(self, name, followers: str = None, following: int = None, public_repos: str = None,
                 public_gists: str = None, token=None):
        self.name = name
        self.followers = followers
        self.following = following
        self.public_repos = public_repos
        self.public_gists = public_gists
        self.contributions = 1

        self.__token = token  # Store token for making API requests. DO NOT INCLUDE IN OUTPUTS.

    def fill_from_json(self, json):
        self.followers = json['followers']
        self.following = json['following']
        self.public_repos = json['public_repos']
        self.public_gists = json['public_gists']

    def to_dict(self):
        return {'name': self.name,
                'followers': self.followers,
                'following': self.following,
                'public_repos': self.public_repos,
                'public_gists': self.public_gists,
                'contributions': self.contributions
                }

    def to_csv_header(self):
        import csv
        import io
        csv_output = io.StringIO()
        # Create a CSV writer
        csv_writer = csv.writer(csv_output, dialect='excel')

        # Write a single row that could be the headers
        csv_writer.writerow(['name', 'followers', 'following', 'public_repos', 'public_gists', 'contributions'])

        # Get the CSV-formatted string from the virtual file
        csv_string = csv_output.getvalue().encode('ascii', 'ignore').decode('ascii')

        csv_output.close()

        return csv_string

    def to_csv_record(self):
        import csv
        import io
        csv_output = io.StringIO()
        # Create a CSV writer
        csv_writer = csv.writer(csv_output, dialect='excel')

        # Write a single row that could be the headers
        csv_writer.writerow(
            [self.name, self.followers, self.following, self.public_repos, self.public_gists, self.contributions])

        # Get the CSV-formatted string from the virtual file
        csv_string = csv_output.getvalue().encode('ascii', 'ignore').decode('ascii')

        csv_output.close()

        return csv_string

    def save_to_csv(self):
        save_as_csv('users.csv', self)


def get_github_api_request(url, convert_json=True, params=None, time_window_days=None, token=None):
    import requests
    if time_window_days is not None:
        import datetime
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=time_window_days)

    if convert_json:
        results = list()
    else:
        results = str()
    another_page = True

    while another_page:
        if token is None:
            # Make a GET request to retrieve pull requests
            response = requests.get(url)
        else:
            # Headers including the Authorization token
            headers = {"Authorization": f"token {token}"}

            # Make a GET request to retrieve pull requests
            response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            if convert_json:
                if type(response.json()) is list:
                    results.extend(response.json())
                else:
                    results = response.json()
            else:
                results = results + response.text

        elif response.status_code == 401:
            raise PermissionError(
                'Server Error 401: Access to Github API denied. You may be using an expired access token.'
                'Create new token at https://github.com/settings/tokens?type=beta. Read more: \n\n' + response.text)
        elif response.status_code == 403:
            raise PermissionError('Server Error 403: Access to Github API denied. Consider creating and using an'
                                  ' authentication token https://github.com/settings/tokens?type=beta. Read more: \n\n' + response.text)
        elif response.status_code == 404:
            raise ValueError('Error 404: No data found at this URL')

        else:
            raise ConnectionError(
                f"Failed to access Github API. Status code: {response.status_code} \n\n" + response.text)

        if 'next' in response.links:  # check if there is another page of results
            if time_window_days is not None:
                last_date_downloaded = datetime.datetime.strptime(results[-1]['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                if last_date_downloaded <= cutoff_date:
                    another_page = False
                    # Filter by date
                    results = [record for record in results if
                               datetime.datetime.strptime(record['created_at'], '%Y-%m-%dT%H:%M:%SZ') >= cutoff_date]

            url = response.links['next']['url']
            if type(results) is not list:
                raise ValueError("Can't resolve multi-page dictionary response")
        else:
            another_page = False

    return results


def save_as_csv(file_name, gitdata_object):
    # Check if the file exists
    file_exists = os.path.exists(file_name)
    header = gitdata_object.to_csv_header()
    data = gitdata_object.to_csv_record()

    # Open the file in append mode
    with open(file_name, 'a', newline='') as file:
        # If it's a new file, write the header
        if not file_exists:
            file.write(header)
        else:
            # Write the CSV record
            file.write(data)
