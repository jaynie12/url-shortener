Summary
=======

URL Shortener

This project helps turn long web addresses into short links that are easier to share.

Getting started
---------------

1. Open a terminal in the project folder.
2. Install the project:

	```bash
	pip install -e .
	```

3. Follow the instructions provided by the project to start using it.

Database migrations
-------------------

Configure the database connection using the project settings, then apply all
pending migrations:

	```bash
	alembic upgrade head
	```

Run this command after installing updates that include database migrations.

Docker
------

Build the application image and start the services defined in the Compose
configuration:

	```bash
	docker compose up --build
	```

Stop the services with `Ctrl+C`, then run:

	```bash
	docker compose down
	```

How it works
------------

The app links a short code to the original web address. Opening the short link takes you to that original address.

Caching strategy
----------------

Cache each short-code lookup with an expiry date (time-to-live). Set the expiry when the entry is cached, and remove or refresh the entry once it expires so cached redirects do not remain stale indefinitely. The cache expiry should not change the lifetime of the short link itself; after a cache miss or expiry, look up the short code in the persistent data store and cache the result again.

Project files
-------------

Browse the folders and files in this repository to explore the app. Refer to the project setup files for any additional instructions.


