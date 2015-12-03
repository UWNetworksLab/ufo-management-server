# ufo-management-server

Management Server component of uProxy for Orgs (UfO)

## Status

[![Travis Status](https://travis-ci.org/uProxy/ufo-management-server.svg)](https://travis-ci.org/uProxy/ufo-management-server)
[![Code Health](https://landscape.io/github/uProxy/ufo-management-server/landscape/landscape.svg?style=flat)](https://landscape.io/github/uProxy/ufo-management-server/landscape)

## Tools

UfO is built using the following tools:
 - [Grunt](http://gruntjs.com/) to write the tasks that build uProxy
 - [Python](https://www.python.org/) as the primary language we code in.
 - [Google AppEngine](https://cloud.google.com/appengine/docs) for basic server functionality on Google infrastructure.
 - [Polymer](http://www.polymer-project.org/) for UI.
 - [Travis](https://travis-ci.org/) for continuous integration.
 - [Landscape](https://landscape.io/dashboard) for code health monitoring.

To manage dependencies we use:
 - [Setup Script](https://github.com/uProxy/ufo-management-server/blob/master/setup.sh) to install various python packages, libraries, and appengine as well as configure the development environemnt.
 - [Bower](http://bower.io) to install libraries that we use in the UI
   (specified in `bower.json`) including Polymer.


## Development Setup

For a high level technical overview of UfO, see the [UfO Design Doc](https://docs.google.com/document/d/1M6gL67V2m5xk1pr42-CLh7jJteg74OpHof-14GgLa3U/edit#).

### Prerequisites to Build UfO

Note: you will either need to run these as root, or set the directories they
modify (`/usr/local`) to being editable by your user (`sudo chown -R $USER /usr/local`)

- [git](https://git-scm.com/)
    - Most machines will have git pre-installed. If you need to install git, you can find instructions from the [git website](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
    - For Windows, install the [desktop git app](https://desktop.github.com/), which provides an easy-to-use interface for git.

- [python](https://www.python.org/)
    - Most OSX or Linux machines will have python pre-installed. If you need to install python, you can find instructions from the [python website](https://wiki.python.org/moin/BeginnersGuide/Download). We develop in python version 2.7 (2.7.10 is the latest stable release at the time of writing).

- [pip](http://pip.readthedocs.org/en/stable/)
    - Pip is a package manager for python which we use to install dependencies. If you need to install pip, you can find instructions from the [pip website](http://pip.readthedocs.org/en/stable/installing/). Note: future versions of the setup script will likely install this for you, but is has not yet been implemented.

### Getting UfO Source and Dependencies

#### Setup without Setup.sh

 1. In your terminal, navigate to a directory where you would like to download UfO. E.g., `cd ~/UfO`

 1. Clone the UfO repository: `git clone https://github.com/uProxy/ufo-management-server.git` or `git clone git@github.com:uProxy/ufo-management-server.git` if you have your ssh access to GitHub set up (useful if you use 2-step auth for GitHub, which you should do).

 1. Navigate into UfO's root directory with `cd ufo-management-server`

 1. Setup build tools and third-party dependencies, run `./setup.sh setup_tests`

#### Setup with Setup.sh

 If you already have the setup.sh script but do not have the rest of the code base, this flow is much simpler.

 1. Run `./setup.sh install`

#### Installing Client-Side Components

Currently, the setup script does not account for installing client-side components through bower. Later versions will support this, but it is not yet implemented.

 1. Install bower, with node this is simply `npm install bower`.
 1. Run `bower install` to get the client-side components.

#### Note About Dependency Changes

Note that if any local dependencies have changed (i.e. changes to bower dependencies, updates to pip packages), you will have to remove your appengine directory and run `./setup.sh setup_tests` to update these dependencies.

### Setting Up OAuth

As part of the OAuth flow, the server must present a “secret” in order to prove it is authorized to use the APIs that are associated with this secret. As the super administrator, do the following:

 1. Go to the Google Developer Console.
 1. Create a project.  Example name can be “my-management-server”.
 1. Select the new project. You may need to refresh the page for the new project to appear.
 1. Click to expand “APIs & auth” in the sidebar.
 1. Click on “APIs” in the sidebar, and search for Admin SDK in the search box.
 1. Click on Admin SDK in the search result.  Click on “Enable API” button.
 1. Click on “Credentials” in the sidebar.
 1. Click on “OAuth consent screen” in the top tab. The only required field is “Product name”. Fill it in and click “Save”.
 1. Select “Add credentials” drop-down menu. Select “OAuth 2.0 client ID”.
 1. Select “Web application” for Application type.
   * It’s okay to leave the default name, or enter something more specific to identify who will be using this secret.
 1. Specify the “Authorized JavaScript origins”.
   * https://<my-management-server>.appspot.com
   * http://localhost:<port_number>  (for development purpose, double-check if this needs to be fully-qualified hostname)
 1. Specify the “Authorized redirect URIs”
   * https://<my-management-server>.appspot.com/oauth2callback
   * http://localhost:9999/oauth2callback (for development purpose, double-check if this needs to be fully-qualified hostname)
 1. Click on “Create” button.
 1. Click on the subsequent “OK” button.
   * You can still access the oauth client id/secret later on for server configuration.

### Testing

Our tests run on [Travis](https://travis-ci.org/) for every commit, push, and pull request automatically. To execute the tests locally before commit, perform the following:

 1. Ensure your environment is configured properly. Run `./setup.sh setup_tests` if not.
 1. Execute the tests with your modified code.
   * Run `./setup.sh run_tests` or
   * Run `python -m unittest discover -p "*_test.py"`

### Running the Server

#### Deploying Local Server

Once you have the source code and dependencies in your environment, running the code on your local machine should be very straightforward.

 1. Ensure your environment is configured properly. Run `./setup.sh setup_tests` if not.
 1. Deploy the server locally:
   * Run `<path_to_appengine_sdk>/dev_appserver.py --port=9999 .` Note the trailing period is required.
   * This is typically `../google_appengine/dev_appserver.py --port=9999 .`
 1. The local server can be reached at https://localhost:9999 .
 1. The admin console can be reached at https://localhost:8000 by default.

#### Deploying Cloud Server (Appspot)

 1. Ensure your environment is configured properly. Run `./setup.sh setup_tests` if not.
 1. Deploy the server to the cloud:
   * Deploy directly:
     * Run `<path_to_appengine_sdk>/appcfg.py -A <your-project-name-here> update .` Note the trailing period is required.
     * This is typically `../google_appengine/appcfg.py -A my-management-server update .`
   * Alternatively, the setup script supports the deploying to a test project.
     * `setup.sh deploy`
 1. The cloud server can be reached at https://<your-project-name-here>.appspot.com/ .
 1. The admin console can be reached at https://console.developers.google.com/apis/library?project=<your-project-name-here> .

#### Setting Up the Server After Deployment

Once the server is deployed, the OAuth client id and secret must be setup and users must be added in order to use the server effectively.

To setup OAuth, perform the following:

 1. Have an admin setup your client id and secret in the admin console.
 1. Get your client id and secret in the Google Developer Console by visiting my-management-server project > APIs & auth heading > Credentials page > my-web-client as an admin.
 1. Copy the Client id and secret from Google Developers Console.
 1. Run the setup oauth handler (/setup/oauthclient) before visiting the main page.
   * For local deployment, go to https://localhost:9999/setup/oauthclient
   * For cloud deployment, go to https://<your-project-name-here>.appspot.com/setup/oauthclient
 1. Enter your credentials for the OAuth flow (username and password).
 1. Click Allow to allow the server access.
    * It should display a message of ‘Setup your client_id and client_secret in the datastore.’
 1. Paste in the values copied from Google Developers Console.
 1. Click Submit. This will automatically redirect you to the add user flow in the next subsection.

To add users, perform the following:

1. Run the add users handler (/user/add).
   * For local deployment, go to https://localhost:9999/user/add
   * For cloud deployment, go to https://<your-project-name-here>.appspot.com/user/add
 1. If prompted, enter your credentials for the OAuth flow (username and password) and click Allow.
 1. From here, users can be added via selection from all users in the domain or from the users within a specific group.
    * To get the users within the domain, click `Fetch All Users in Domain`.
    * To get the users within a specific group, input a group key (group email alias) into the input box and click `Fetch Users From Group`.
 1. Once the users within the domain or group are displayed, check the box next to those wished to be added.
 1. Click Add Selected Users to add those users and generate each's token.
    * Note: there is currently no validation of what users are already added to the management server vs what users are attempted to be added. However, re-adding an existing user will only generate a new token for that user and will not create a duplicate entry.

That's it. You should now be able to add more users if desired or start adding proxy servers. The navigation bar should assist in traversing between handlers and back to the main page. Thanks for using UfO!
