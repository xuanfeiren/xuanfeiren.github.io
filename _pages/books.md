---
layout: single
title: "Reading"
permalink: /books/
author_profile: true
---

I keep a reading diary on Douban. This page is synced automatically from my latest marks there, so it always reflects what I am actually reading. Recommendations are very welcome — [drop me an email](mailto:xuanfeir@gmail.com) if we share a taste in books!

{% assign books = site.data.douban | where: "category", "book" %}
{% assign reading = books | where: "status", "reading" %}
{% assign finished = books | where: "status", "read" %}
{% assign wishlist = books | where: "status", "want_to_read" %}
{% assign movies = site.data.douban | where: "category", "movie" %}

{% if reading.size > 0 %}
## Currently Reading

{% for item in reading %}{% include douban-card.html item=item %}{% endfor %}
{% endif %}

{% assign by_year = finished | group_by_exp: "item", "item.date | slice: 0, 4" | sort: "name" | reverse %}
{% for year in by_year %}
## Read in {{ year.name }}

{% for item in year.items %}{% include douban-card.html item=item %}{% endfor %}
{% endfor %}

{% if wishlist.size > 0 %}
## Want to Read

{% for item in wishlist %}{% include douban-card.html item=item %}{% endfor %}
{% endif %}

{% if movies.size > 0 %}
## Beyond Books

Movies I watched recently:

{% for item in movies %}{% include douban-card.html item=item %}{% endfor %}
{% endif %}
