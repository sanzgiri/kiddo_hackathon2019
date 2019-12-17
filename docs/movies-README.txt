(first operation to get movies from laabeled data)

grep -oh -E  '/movie-reviews/[^"]+' attributes/*.html  | sort -u   > movies-list.txt

 wget -r -i ../movies-list.txt --random-wait -w 3 -nH -k --no-parent -I /movie-reviews -nc -L -E --reject-regex ".*\?width=.*" -R robots.txt -B https://www.commonsensemedia.org

(repeat this operation to get new sets)

grep -oh -E  '/movie-reviews/[^"]+' movies/movie-reviews/*.html | grep -v 'width=' | grep -v '&quot' |  grep -v -e '/adult$' | grep -v -e '/child$' | sort -u > movies-list-extra.txt

diff movies-list.txt movies-list-extra.txt | grep -e '^> ' | sed -e 's@^> @@g' > movies-list-delta.txt

(then reun theh "wget" command above)

(then update the movies-list file)
mv movies-list-extra.extra.txt movies-list.txt


(mining from master movie listing)
for i in $(seq 490); do wget "https://www.commonsensemedia.org/movie-reviews?sort=field_canonical_date&order=desc&page=$i" --random-wait -w 3 -nH -k --no-parent -nc ; done



(crawling IMDB list)
(hint from here -- https://unix.stackexchange.com/questions/61132/how-do-i-use-wget-with-a-list-of-urls-and-their-corresponding-output-files)

diff imdb-urls.txt imdb-urls.new.txt | grep '^> ' | sed -e 's@^> @@g' > imdb-urls-delta.txt

while read -r url filename tail; do  wget -O "$filename.html" "$url"  --random-wait -w 3 -nH -k --no-parent -nc -L -E  -R robots.txt  ; done < ../imdb-urls-delta.txt



(old work)
Attempted to use labeled method for scraping..
https://github.com/scrapy/scrapely
https://support.scrapinghub.com/support/solutions/articles/22000201027-learn-portia-video-tutorials-


