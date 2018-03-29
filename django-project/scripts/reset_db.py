"""
Script that resets the django-project database.

The script "removes" the database file, db.sqlite3, by renaming it to
db.sqlite3.cp. The script "removes" the migrations files of each app by moving
them to the project level directory and renaming them app-name_migrations.

The script then runs makemigrations on with each app explicitly named as an
argument and then finally runs migrations.
"""
import os
import sys
import shutil
import subprocess

SUCCESS = 0

def main():

    # Rename db.sqlite3
    db_src_file = "db.sqlite3"
    db_dst_file = "db.sqlite3.cp"
    try:
        os.rename(db_src_file, db_dst_file)
    except OSError as ose:
        print("\n".join([
            "A file db.sqlite3.cp already exists.",
            "Please remove it before proceeding."
        ]))
        sys.exit(1)

    apps = ["dishes", "accounts"]

    for app in apps:
        # Move the app migrations directory to the
        # project level directory.
        app_src = os.path.join(app, "migrations")
        app_dst = "_".join([app, "migrations"])
        try:
            os.rename(app_src, app_dst)
        except OSError as ose:
            print("\n".join([
                "A directory {app_dst} already exists.",
                "Please remove it before proceeding."
            ]).format(app_dst=app_dst))
            sys.exit(1)

    for app in apps:
        # Run makemigrations
        cmp_proc = subprocess.run(["python",
                                   "manage.py",
                                   "makemigrations",
                                   app])
        if cmp_proc.returncode != SUCCESS:
            print("An error occurred running makemigrations",
                  "for the Django app {app}".format(app=app))
            sys.exit(1)

    # Run migrate
    cmp_proc = subprocess.run(["python", "manage.py", "migrate"])

if __name__ == "__main__":
    main()
