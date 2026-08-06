---
layout: single
title: "Reading"
permalink: /books/
author_profile: true
---

I keep a reading diary on [Douban](https://www.douban.com/people/191702958/). This page is synced automatically from my latest marks there, so it always reflects what I am actually reading. Recommendations are very welcome — [drop me an email](mailto:xuanfeir@gmail.com) if we share a taste in books!

{% assign books = site.data.douban | where: "category", "book" %}
{% assign reading = books | where: "status", "reading" %}
{% assign finished = books | where: "status", "read" %}
{% assign wishlist = books | where: "status", "want_to_read" %}
{% assign movies = site.data.douban | where: "category", "movie" %}

{% if reading.size > 0 %}
## Currently Reading

{% for item in reading %}{% include douban-card.html item=item %}{% endfor %}
{% endif %}

{% if finished.size > 0 %}
## Recently Finished

{% for item in finished %}{% include douban-card.html item=item %}{% endfor %}
{% endif %}

{% if wishlist.size > 0 %}
## Want to Read

{% for item in wishlist %}{% include douban-card.html item=item %}{% endfor %}
{% endif %}

{% if movies.size > 0 %}
## Beyond Books

Movies I watched recently:

{% for item in movies %}{% include douban-card.html item=item %}{% endfor %}
{% endif %}
