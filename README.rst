Kiddos
######

*Kurated Informative Documents Describing Our Society*

A project to help parents, children, and social explorers to discover content by impactful filters.  

* `Background`_
* `Technology`_
* `Future`_
* `Team`_

Background
==========
Talk about the objective, kid-centric, curated list pruning.


Technology
==========
Talk about using NLP, scrape, streamlit.

Interested in running it yourself? Just install streamlit and then run the app from its directory...

.. code-block:: 

    pip install streamlit
    cd app; streamlit run kiddos.py


Adding Score Data
-----------------
The app uses columnar score data in individual CSVs to make editing easier.  If you want to fill or 
replace one of the existing categories, check out the directory `data/score_data` in this repo and
*only if it's a new file* follow these simple directions to get it added to git/lfs.

.. code-block:: 
    git lfs track data/score_data/NEWFILE.csv
    git add data/score_data/NEWFILE.csv -f


Future
======
Talk about future directions we could go for business, other usages, etc.

* Business examples
   * **Engagement**: Finding the impact and meaningfulness of different social issues versus engagement;  here, we can link the data with sources that indicate viewership or financial gross for attendance
* User Examples
   * **Catalog Suggest**: Go beyond what's on our catalog, but allow users to suggest that it's added to the catalog.


Team
====
This team of collaborators spans locations and internal companies. 

* **Jianxiong Dong** - Like to develop scalable data mining tools and build customer-focused machine learning applications (Principal Inventive Scientist, Data Science and AI Research, AT&T, San Ramon, CA)
* **Sam Lee** - Sam Lee - Loves dogs and video games. Sell-Side and Marketplace Data Science. (Data Scientist, Data Science, Xandr, San Ramon, CA)
* **Ashutosh Sanzgiri** - Content & Contextual Intelligence (Senior Data Scientist, Xandr, Portland, WA)
* **Eric Zavesky** - Video analytics and machine learning veteran with a user-centric focus.  Seeking to use automation and guidance to solve problems in content, XR, IoT and robtics.  (Principal Inventive Scientist, Data Science and AI Research, AT&T, Austin, TX)

