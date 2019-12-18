# Imports
import streamlit as st
import pandas as pd
import numpy as np
import ast
from os import path
from pathlib import Path
import re
import hashlib

data_dir = path.join("..", "data")
score_dir = path.join(data_dir, "score_data")
version_path = path.join("..", "_version.py")
joint_scoring = True  # toggle whether we use full depth scores or single CSV
re_issue = re.compile(r"[^0-9A-Za-z]+")
presence_bars = False  # toggle to show presence indicators as a graph
issue_titles = 10   # how many titles to show on single issue

def simple_score(str_source):
    return f"score_{re_issue.sub(r'_', str_source)}"

def main_page():
    # read in version information
    version_dict = {}
    with open(version_path) as file:
        exec(file.read(), version_dict)
    
    # Create the title
    st.markdown(f"""<div style="font-size:5pt; font-weight:100; text-align:center; width=100%;">
                     <span style="font-size:40pt;">{version_dict['__project__']}</span><br>
                     <span style="font-size:15pt; color:#a1a1a1;">{version_dict['__description__']} 
                        (v {version_dict['__version__']})</span></div>""", unsafe_allow_html=True)

    # Prompt User to enter a topic they'd like to discuss
    st.markdown('<div style="text-align:center; font-size:12pt;"><br><br>I want to talk to my kids about...</div>',
                unsafe_allow_html=True)

    all_issues = "Everything!"
    issues_list = [all_issues,
                   'Bullying',
                   'Civil Rights',
                   'Civic Engagement',
                   'Climate Change',
                   'Gender Equality',
                   'Gun Control',
                   'Homelessness',
                   'Immigration',
                   'LGBTQ+',
                   'Substance Abuse',
                   'Sustainability']
    option = st.selectbox('', issues_list)

    # Pull in the trending data
    trendlines_df = pd.read_csv(path.join(data_dir, 'trend30.csv'))
    
    # load data, allowing for a cache
    trending_df = data_load("data_bundle", True)

    # Have a little party
    btn = st.button('I found a useful movie!')
    if btn:
        st.balloons()

    st.markdown('<br><br><hr>',
                unsafe_allow_html=True)

    # If the user hasn't chosen a topic, show the top videos by trending topic
    if option == all_issues:
        new_trending_df = draw_sidebar(trending_df)

        # Filter to the top titles for each social issue
        new_trending_df = new_trending_df.sort_values(['avg_score','original_release_year'], ascending=False)
        
        # Show the titles
        st.markdown(
            '<br><br><div style="font-size: 22pt; font-weight:100; text-align:center; margin-left: 30%; width:40%; border-bottom: 0.5pt #a1a1a1 solid;">Trending Topics</div><br>',
            unsafe_allow_html=True)

        # Find the order to display the issues based on their relative relevance
        last_date_df = trendlines_df[trendlines_df.Date == trendlines_df.Date.max()]
        del last_date_df['Date']
        last_date_df = last_date_df.T.reset_index().sort_values(len(trendlines_df.index) - 1, ascending=False).rename(
            columns={'index': 'social_issue'})

        trending_issues = last_date_df.social_issue.dropna().unique().tolist()

        # graphics or text for scores
        presence_mode = "Text"
        if presence_bars:
            presence_mode = st.sidebar.radio("Presence Display", ("Text", "Bar Chart"))

        # For each social issue, show the top video
        for issue in trending_issues:
            title_df = []
            if joint_scoring:  # sort by score (should already obey other sort criterion)
                simple_score_str = simple_score(issue)
                if simple_score_str in new_trending_df.columns:
                    title_df = new_trending_df.sort_values(simple_score_str, ascending=True).head(1)
                    # print(f"SORT: {simple_score_str}, issue:{issue}, score:{title_df.head(1)[simple_score_str]}, min:{title_df[simple_score_str].min()}, max:{title_df[simple_score_str].max()}, first:{title_df.head(1)}")
            else:  # already sorted above
                title_df = new_trending_df[new_trending_df['social_issue'] == issue]
            if len(title_df):
                st.markdown('<div>' + \
                            '  <div style="display:inline-block; width:50%;">' + \
                            f'    <span style="font-size:18pt; font-weight:600;">&emsp;&emsp;{issue.replace("_", " ").title()}</span>'
                            '  </div><br><br><br>' + \
                            '  <div style="width:80%; text-align:center;">' + \
                            '     <span style="font-size:8pt; text-align:center;">Trending Activity:</span><br><br>',
                            unsafe_allow_html=True)

                # Shows the trend for the issue
                st.line_chart(trendlines_df.set_index('Date')[[issue]].rename(columns={issue: 'Relative Interest'}),
                              width=700,
                              height=10)
                st.markdown('  </div><br><br><br><br>' + \
                            '</div>',
                            unsafe_allow_html=True)

                draw_title(title_df, presence_mode)

                st.markdown('<br><br><br>',
                            unsafe_allow_html=True)

    # If the user chooses an issue to dig into, do this
    else:
        sort_list = [('avg_score',False), ('original_release_year', False)]
        
        # Filter to the issue and make sure that there is associated data. If there isn't default to just send the user to HBO
        if joint_scoring:  # sort by score (should already obey other sort criterion)
            trending_df2 = trending_df
            sort_list.insert(0, (simple_score(option), True))
        else:  # already sorted above
            trending_df2 = trending_df[trending_df['social_issue'] == option]
            sort_list.insert(0, (trending_df['social_issue'], True))
            
        if len(trending_df2) > 1:
            new_trending_df = draw_sidebar(trending_df, trending_df2, sort_list)

            # graphics or text for scores
            presence_mode = "Text"
            if presence_bars:
                presence_mode = st.sidebar.radio("Presence Display", ("Text", "Bar Chart"))

            # Find if the data still has titles present, if not, default to send user to HBO
            if len(new_trending_df):
                title_df = new_trending_df.head(issue_titles)  # grab top N results
                st.markdown('<div>' + \
                            '  <div style="display:inline-block; width:50%;">' + \
                            f'    <span style="font-size:18pt; font-weight:600;">&emsp;&emsp;{option.replace("_", " ").title()}</span>'
                            '  </div><br><br><br>',
                            unsafe_allow_html=True)

                # Show the top 10 titles for the issue based on average score
                for title in list(title_df["title"]):
                    # Check that there is actually data
                    draw_title(title_df[title_df["title"] == title], presence_mode)
                    
                # end of main function
                st.markdown(f"""<br /><div style="text-align:center; width=100%;">
                                    <span style="font-size:small; color:#8e8e8e;">
                                (about {len(new_trending_df)} matching titles)</span></div>""",
                            unsafe_allow_html=True)

        else:
            st.markdown(
                '<div style="width:100%; text-align: center; font-size:20pt; padding-top: 50px;">No Options...but there are a lot of great shows on <a href="https://play.hbonow.com/"><img style="width:350px; height:150px; display:inline-block;" src="data:image/png;base64,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"></a></div>',
                unsafe_allow_html=True)
      
    # end of main function
    st.markdown(f"""<br /><div style="text-align:center; width=100%;">
                        <span style="font-size:small; color:#a1a1a1;">{version_dict['__author__']}
                            <br /><em>collaborators</em></span></div>""",
                unsafe_allow_html=True)

    # end of main function
    pass
    
    
def data_load(stem_datafile, allow_cache=True):
    """Because of repetitive loads in streamlit, a method to read/save cache data according to modify time."""

    # generate a checksum of the input files
    m = hashlib.md5()
    for filepath in Path(data_dir).rglob(f'*.csv'):
        m.update(str(filepath.stat().st_mtime).encode())

    # NOTE: according to this article, we should use 'feather' but it has depedencies, so we use pickle
    # https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d
    path_new = path.join(data_dir, f"{stem_datafile}.{m.hexdigest()[:8]}.pkl")

    # see if checksum matches the datafile (plus stem)
    if allow_cache and path.exists(path_new):
        # if so, load old datafile, skip reload
        return pd.read_pickle(path_new)
        
    print(f"Data has changed, regenerating core data bundle file {path_new}...")
    
    # if not, delete old file reload all data
    for filepath in Path(data_dir).rglob(f'{stem_datafile}*.feather'):
        filepath.unlink()
    
    # Pull in the data about the movies
    trending_df = pd.read_csv(path.join(data_dir, 'app_data.tsv'), sep='\t')

    # Pull in the matching movie to social issue data and merge
    trending_df['imdb_id'] = trending_df['imdb_id'].str.replace('tt','').astype(int)  # convert to int
    if joint_scoring:  # merge the CSV files embedded
        trending_df.set_index('imdb_id', drop=True, inplace=True)
        for filename in Path(score_dir).rglob(f'*.csv'):
            score_issue_str = simple_score(Path(filename).stem)
            if score_issue_str in trending_df.columns:
                print(f"Warning {filename}, already loaded as {score_issue_str}")
                
            print(f"Reading {filename}")
            match_df = pd.read_csv(filename, dtype=str)
            match_df['imdb_id'] = match_df['imdb_id'].str.replace('tt','').astype(int)
            match_df.drop_duplicates('imdb_id', inplace=True)
            # print(f"AAA new: {len(match_df)}")
            match_df['imdb_id'] = match_df['imdb_id'].astype(int)  # coerce to int
            match_df.set_index('imdb_id', drop=True, inplace=True)
            match_df.rename(inplace=True, columns={'inf_dist_summary': score_issue_str})
            match_df[score_issue_str] = match_df[score_issue_str].astype(float)

            # directly insert via index
            listMerge = set(trending_df.index).intersection(set(match_df.index))
            trending_df[score_issue_str] = np.inf
            # print( match_df.loc[listMerge, [score_issue_str]])
            trending_df.loc[listMerge, [score_issue_str]] = match_df.loc[listMerge, [score_issue_str]]
            # print(trending_df.loc[listMerge, [score_issue_str]])
            #print(trending_df.dtypes)
            pass   # skip to next item
    else:  # prior method to load issue matching file
        match_df = pd.read_csv(path.join(data_dir, 'issue_matching.csv'))
        # match_df.set_index('imdb_id', drop=True, inplace=True)
        trending_df = trending_df.merge(match_df[['imdb_id', 'social_issue','match_score']])
        
    # debug print a few rows for diversity
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(trending_df.sample(3))
    
    # Process data to proper format
    trending_df = trending_df.rename(columns={'release_year': 'original_release_year',
                                              'hbogo_url': 'hbo_url',
                                              'short_desc': 'summary'})
    trending_df['scores'] = trending_df['scores'].fillna('{}')

    # now, extract age from the data for another slider (from age 8+); added 0.9.3
    trending_df["age_number"] = trending_df.age_child.fillna('0').str.replace('None', '0')
    trending_df["age_number"] = trending_df.age_number.str.replace(r'age (\d+)\+', r'\1').astype(int)
    

    # Adjust scores to be a column per score
    trending_df_split = [ast.literal_eval(trending_df.iloc[i]['scores']) for i in range(len(trending_df))]
    trending_df_split = pd.DataFrame(trending_df_split, index=trending_df.index)
    trending_df = trending_df.join(trending_df_split)
    trending_df = trending_df.rename(columns={'Consumerism': 'consumerism_score',
                                              'Drinking, Drugs & Smoking': 'drinking_drugs_smoking_score',
                                              'Language': 'language_score',
                                              'Positive Messages': 'positive_messages_score',
                                              'Positive Role Models & Representations': 'positive_role_models_score',
                                              'Sex': 'sex_score',
                                              'Violence': 'violence_score',
                                              'Educational Value': 'educational_value_score',
                                              'Sexy Stuff': 'sexy_stuff_score',
                                              'Violence & Scariness': 'violence_scariness_score'})

    # Fill missing data with defaults
    trending_df['hbo_url'] = trending_df['hbo_url'].fillna('https://play.hbonow.com/')
    trending_df['movie_trailer_url'] = trending_df['movie_trailer_url'].fillna('https://play.hbonow.com/')
    trending_df['age_child'] = trending_df['age_child'].fillna('Not Set')
    trending_df = trending_df[~trending_df['title'].astype(str).str.contains('{')]

    # Fill missing scores with 0
    all_scores = ['consumerism_score','positive_messages_score','positive_role_models_score','educational_value_score','violence_score','sex_score','language_score','consumerism_score','drinking_drugs_smoking_score','sexy_stuff_score','violence_scariness_score']
    for score in all_scores:
        trending_df[score] = trending_df[score].fillna(0).astype(int)
        trending_df[score] = np.where(~trending_df[score].isin([1,2,3,4,5]), 0, trending_df[score])

    # Invert "negative" scores so they can be assessed similarly to the "positive" scores
    neg_scores = ['violence_score','sex_score','language_score','consumerism_score','drinking_drugs_smoking_score','sexy_stuff_score','violence_scariness_score']
    for neg_score in neg_scores:
        trending_df['neg_' + neg_score] = np.where(trending_df[neg_score] == 1, 5,
                                                   np.where(trending_df[neg_score] == 2, 4,
                                                            np.where(trending_df[neg_score] == 4, 2,
                                                                     np.where(trending_df[neg_score] == 5, 1,
                                                                              trending_df[neg_score]))))

    # Calculate a VERY basic average score for each title
    trending_df['non_zero_scores'] = trending_df[all_scores].astype(bool).sum(axis=1) + 1
    trending_df = trending_df.dropna()
    trending_df['original_release_year'] = trending_df['original_release_year'].astype(int)
    trending_df['avg_score'] = ((trending_df[['positive_messages_score',
                                              'positive_role_models_score',
                                              'educational_value_score',
                                              'neg_violence_score',
                                              'neg_sex_score',
                                              'neg_language_score',
                                              'neg_consumerism_score',
                                              'neg_drinking_drugs_smoking_score',
                                              'neg_sexy_stuff_score',
                                              'neg_violence_scariness_score']].sum(axis=1) /
                                          trending_df['non_zero_scores'].astype(float) )).round(1)

    # (trending_df['match_score'])).astype(float)/np.where(trending_df['non_zero_scores'] == 0, 1, trending_df['non_zero_scores'])).round(1).astype(float)

    # save new data file before returning
    trending_df.to_pickle(path_new)
    return trending_df


def draw_title(title_df, presence_mode="Text"):
    if len(title_df):
        title = title_df.title.values[0]
        summary = title_df.summary.values[0]
        avg_score = title_df.avg_score.values[0]
        hbo_url = title_df.hbo_url.values[0]
        movie_trailer_url = title_df.movie_trailer_url.values[0]
        poster = title_df.poster.values[0]

        list_print = ['<div style="width:100%;">' + \
                    '  <div style="display:inline-block; width:20%;">' + \
                    f'    <div style="display:inline-block; width:50px;"></div><img style="display:inline-block;" src="{poster}" width:50px; height:100px;>'
                    '  </div>' + \
                    '  <div style="display:inline-block; padding-left: 50px; vertical-align:top; width: 50%;">' + \
                    f'    <span style="font-size:12pt;">{title}</span><br>' + \
                    f'    <span style="font-size: 10pt; color:#a1a1a1;">{summary[:200]}...<a style="color:#a1a1a1; font-size:8pt; font-weight:600;"> Read More</a></span><br>']
                  
  
        # may still be inefficienttttt but blegh
        list_print.append(f'<span style="font-size: 10pt;">Recommended Age: {title_df.age_child.values[0]}</span>')
        list_print.append(f'<span style="font-size: 10pt;">Release Year: {title_df.original_release_year.values[0]}</span>')

        # start walking through individual scores
        list_print.append(f'<span style="font-size: 10pt; font-weight:600;">Presence Scores (out of 5):</span>')

        score_list = [("Positive Messages",'positive_messages_score'), ("Positive Role Models",'positive_role_models_score'), 
            ("Educational Value",'educational_value_score'), ("Violence",'violence_score'), 
            ("Violence and Scariness",'violence_scariness_score'), ("Sex",'sex_score'), 
            ("Sexy Stuff",'sexy_stuff_score'), ("Language",'language_score'), 
            ("Consumerism",'consumerism_score'), ("Drinking, Drugs & Smoking",'drinking_drugs_smoking_score')]

        for score_item in score_list:  # loop through each item
            if hasattr(title_df, score_item[1]):
                if presence_mode == "Text":
                    score_value = getattr(title_df, score_item[1]).values[0]
                    if score_value > 0:  # don't include zero value items
                        list_print.append(f'<span style="font-size: 10pt;">{score_item[0]}: {score_value}</span>')
                else:
                    print(f"PRESENCE MODE {presence_mode} NOT AVAILABLE YET")
        
        # add our streaing links
        list_print.append(f'     <br><span style="font-size: 10pt; font-weight:600; display:inline-block;">Watch now it on&emsp; </span><a href="{hbo_url}"><img style="width:35px; height:15px; display:inline-block;" src="data:image/png;base64,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"></a>' + \
                    f'     &emsp;<span style="font-size: 10pt; font-weight:600; display:inline-block;">or</span>&emsp;<a href="{hbo_url}"><img style="width:35px; height:20px; display:inline-block;" src="data:image/png;base64,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"></a>' + \
                    f'     &emsp;<span style="font-size: 10pt; font-weight:600; display:inline-block;">Watch a trailer on </span>&emsp;<a href="{movie_trailer_url}"><img style="width:60px; height:25px; display:inline-block;" src="data:image/png;base64,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"></a>' + \
                    '  </div>' + \
                    '  <div style="display:inline-block; padding-left:30px; float:right; vertical-align:top; width:25%; padding-top:30px;">' + \
                    f'    <div style="width:100%; padding-top: 10px; color:white; height: 150px; background-color: #a6a7a8; text-align:center; font-size:10pt;">Average Acceptability Score<br><span style="font-size:30pt; color:white;">{avg_score}</span>' + \
                    '    </div>' + \
                    '  </div>' + \
                    '</div>')
    
        list_print.append("<br >")

        # Actually display the title details
        st.markdown("\n<br >".join(list_print), unsafe_allow_html=True)

    else:
        st.markdown('<div style="width:100%; text-align: center; font-size:20pt; padding-top: 50px;">No Options...but there are a lot of great shows on <a href="https://play.hbonow.com/"><img style="width:350px; height:150px; display:inline-block;" src="data:image/png;base64,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"></a></div>',
                 unsafe_allow_html=True)
    # end function for drawing
    pass


def draw_sidebar(trending_df, trending_df2=None, sort_list=None):
    if trending_df2 is None:   # handle the generic case
        trending_df2 = trending_df
   
    # Generate the slider filters based on the data available in this subset of titles
    # Only show the slider if there is more than one value for that slider, otherwise, don't filter
    st.sidebar.title('Discovery Filters')
    st.sidebar.markdown("<br>",
                        unsafe_allow_html=True)
    if trending_df2.original_release_year.min() != trending_df2.original_release_year.max():
        value = (int(trending_df2.original_release_year.min()), int(trending_df2.original_release_year.max()))
        release_year = st.sidebar.slider('Release Year',
                                     min_value=int(trending_df2.original_release_year.min()),
                                     max_value=int(trending_df2.original_release_year.max()),
                                     value=value,
                                     step=1)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        release_year = (0,5)
    if trending_df2.avg_score.min() != trending_df2.avg_score.max():
        value = (trending_df2.avg_score.min(), trending_df2.avg_score.max())
        avg_score = st.sidebar.slider('Average Acceptability Score',
                                  min_value=trending_df2.avg_score.min(),
                                  max_value=trending_df2.avg_score.max(),
                                  value=value,
                                  step=0.5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        avg_score = (0,5)

    # added 0.9.3, filtering on int-based age
    if trending_df2.age_number.min() != trending_df2.age_number.max():
        value = (float(trending_df2.age_number.min()), float(trending_df2.age_number.max()))
        age_number = st.sidebar.slider('Age',
                                               min_value=float(trending_df2.age_number.min()),
                                               max_value=float(trending_df2.age_number.max()),
                                               value=value,
                                               step=0.5)
    else:
        age_number = (0,5)        
        
    if trending_df2.positive_messages_score.min() != trending_df2.positive_messages_score.max():
        value = (float(trending_df2.positive_messages_score.min()), float(trending_df2.positive_messages_score.max()))
        positive_messages = st.sidebar.slider('Positive Messages Score',
                                           min_value=float(trending_df2.positive_messages_score.min()),
                                           max_value=float(trending_df2.positive_messages_score.max()),
                                           value=value,
                                           step=0.5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        positive_messages = (0,5)
    if trending_df2.positive_role_models_score.min() != trending_df2.positive_role_models_score.max():
        value = (float(trending_df2.positive_role_models_score.min()), float(trending_df2.positive_role_models_score.max()))
        positive_role_models = st.sidebar.slider('Positive Role Models Score',
                                              min_value=float(trending_df2.positive_role_models_score.min()),
                                              max_value=float(trending_df2.positive_role_models_score.max()),
                                              value=value,
                                              step=0.5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        positive_role_models = (0,5)
    if trending_df2.educational_value_score.min() != trending_df2.educational_value_score.max():
        value = (int(trending_df2.educational_value_score.min()), int(trending_df2.educational_value_score.max()))
        educational_value = st.sidebar.slider('Educational Value Score',
                                              min_value=int(trending_df2.educational_value_score.min()),
                                              max_value=int(trending_df2.educational_value_score.max()),
                                              value=value,
                                              step=1)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        educational_value = (0,5)
    if trending_df2.violence_score.min() != trending_df2.violence_score.max():
        value = (float(trending_df2.violence_score.min()), float(trending_df2.violence_score.max()))
        violence = st.sidebar.slider('Violence Score',
                                 min_value=float(trending_df2.violence_score.min()),
                                 max_value=float(trending_df2.violence_score.max()),
                                 value=value,
                                 step=0.5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        violence = (0,5)
    if trending_df2.violence_scariness_score.min() != trending_df2.violence_scariness_score.max():
        value = (int(trending_df2.violence_scariness_score.min()), int(trending_df2.violence_scariness_score.max()))
        violence_scariness = st.sidebar.slider('Violence and Scariness Score',
                                 min_value=int(trending_df2.violence_scariness_score.min()),
                                 max_value=int(trending_df2.violence_scariness_score.max()),
                                 value=value,
                                 step=5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        violence_scariness = (0,5)

    if trending_df2.sex_score.min() != trending_df2.sex_score.max():
        value = (float(trending_df2.sex_score.min()), float(trending_df2.sex_score.max()))
        sex = st.sidebar.slider('Sex Score',
                            min_value=float(trending_df2.sex_score.min()),
                            max_value=float(trending_df2.sex_score.max()),
                            value=value,
                            step=0.5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        sex = (0, 5)
    if trending_df2.sexy_stuff_score.min() != trending_df2.sexy_stuff_score.max():
        value = (int(trending_df2.sexy_stuff_score.min()), int(trending_df2.sexy_stuff_score.max()))
        sexy_stuff = st.sidebar.slider('Sexy Stuff Score',
                            min_value=int(trending_df2.sexy_stuff_score.min()),
                            max_value=int(trending_df2.sexy_stuff_score.max()),
                            value=value,
                            step=1)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        sexy_stuff = (0, 5)
    if trending_df2.language_score.min() != trending_df2.language_score.max():
        value = (float(trending_df2.language_score.min()), float(trending_df2.language_score.max()))
        language = st.sidebar.slider('Language Score',
                                 min_value=float(trending_df2.language_score.min()),
                                 max_value=float(trending_df2.language_score.max()),
                                 value=value,
                                 step=0.5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        language = (0,5)
    if trending_df2.consumerism_score.min() != trending_df2.consumerism_score.max():
        value = (float(trending_df2.consumerism_score.min()), float(trending_df2.consumerism_score.max()))
        consumerism = st.sidebar.slider('Consumerism Score',
                                    min_value=float(trending_df2.consumerism_score.min()),
                                    max_value=float(trending_df2.consumerism_score.max()),
                                    value=value,
                                    step=0.5)
        st.sidebar.markdown("<br>",
                            unsafe_allow_html=True)
    else:
        consumerism = (0,5)
    if trending_df2.drinking_drugs_smoking_score.min() != trending_df2.drinking_drugs_smoking_score.max():
        value = (float(trending_df2.drinking_drugs_smoking_score.min()), float(trending_df2.drinking_drugs_smoking_score.max()))
        drinking_drugs_smoking = st.sidebar.slider('Drinking, Drugs & Smoking Score',
                                               min_value=float(trending_df2.drinking_drugs_smoking_score.min()),
                                               max_value=float(trending_df2.drinking_drugs_smoking_score.max()),
                                               value=value,
                                               step=0.5)
    else:
        drinking_drugs_smoking = (0,5)
        
    # print(f"Sort criterion: {sort_list}")

    # Filter by slider inputs to only show relevant titles
    new_trending_df = trending_df2[(trending_df2['original_release_year'] >= release_year[0]) &
                                   (trending_df2['original_release_year'] <= release_year[1]) &
                                   (trending_df2['avg_score'] >= avg_score[0]) &
                                   (trending_df2['avg_score'] <= avg_score[1]) &
                                   (trending_df2['age_number'] >= age_number[0]) &
                                   (trending_df2['age_number'] <= age_number[1]) &
                                   (trending_df2['positive_messages_score'] >= positive_messages[0]) &
                                   (trending_df2['positive_messages_score'] <= positive_messages[1]) &
                                   (trending_df2['positive_role_models_score'] >= positive_role_models[0]) &
                                   (trending_df2['positive_role_models_score'] <= positive_role_models[1]) &
                                   (trending_df2['violence_score'] >= violence[0]) &
                                   (trending_df2['violence_score'] <= violence[1]) &
                                   (trending_df2['sex_score'] >= sex[0]) &
                                   (trending_df2['sex_score'] <= sex[1]) &
                                   (trending_df2['language_score'] >= language[0]) &
                                   (trending_df2['language_score'] <= language[1]) &
                                   (trending_df2['consumerism_score'] >= consumerism[0]) &
                                   (trending_df2['consumerism_score'] <= consumerism[1]) &
                                   (trending_df2['drinking_drugs_smoking_score'] >= drinking_drugs_smoking[0]) &
                                   (trending_df2['drinking_drugs_smoking_score'] <= drinking_drugs_smoking[1]) &
                                   (trending_df2['sexy_stuff_score'] >= sexy_stuff[0]) &
                                   (trending_df2['sexy_stuff_score'] <= sexy_stuff[1]) &
                                   (trending_df2['educational_value_score'] >= educational_value[0]) &
                                   (trending_df2['educational_value_score'] <= educational_value[1]) &
                                   (trending_df2['violence_scariness_score'] >= violence_scariness[0]) &
                                   (trending_df2['violence_scariness_score'] <= violence_scariness[1])]

    # hard work done, return the trends!
    if sort_list is None:
        return new_trending_df
    # otherwise apply sorting right now
    return new_trending_df.sort_values(by=[v[0] for v in sort_list], 
                                       ascending=[v[1] for v in sort_list])


# main block run by code
if __name__ == '__main__':
    main_page()
