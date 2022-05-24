# How to contribute

## Make Changes

* In your forked repository, create a topic branch for your upcoming patch. (e.g. `feature/autoplay` or `fix/upload-photos-not-saved`)
	* Usually this is based on the main branch.
	* Create a branch based on main; `git branch
	fix/my_contribution main` then checkout the new branch with `git
	checkout fix/my_contribution`.  Please avoid working directly on the `main` branch.
* Make sure you stick to the coding style that is used already.
* Make commits of logical units and describe them properly.

* Make sure pre-commit hooks are installed using `pre-commit install` and run it on staged files.
* Generate migration files using `flask db migrate -m "migration message"` upon any changes to data models.

* If possible, submit tests to your patch / new feature so it can be tested easily.
* Run tests using tox or pytest, get test coverage using coverage.
* Assure nothing is broken by running all the tests.

* Serve and test the production server using gunicorn: `gunicorn server:app` (optional)

## Submit Changes

* Push your changes to a topic branch in your fork of the repository.
* Open a pull request to the original repository and choose the right original branch you want to patch.
* If not done in commit messages (which you really should do) please reference and update your issue with the code changes. But _please do not close the issue yourself_.
* Even if you have write access to the repository, do not directly push or merge pull-requests. Let another team member review your pull request and approve.

# Project Setup

* Install pipenv, python 3.8, postgresql 13 and gunicorn (optional).
	- Gunicorn is used for production deployment only.
	- Recommendation: use pyenv for management of multiple python versions.
* Configure `.env` file, see [`.env.example`](./.env.example) for reference.
* Create virtual environment with pipenv.
* Apply migrations to database `flask db upgrade`

# Additional Resources

* [General GitHub documentation](http://help.github.com/)
* [GitHub pull request documentation](https://help.github.com/articles/about-pull-requests/)
