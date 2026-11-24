FROM httpd:2.4

RUN sed -i -E \
    's/^#(LoadModule (rewrite|headers|expires|deflate|filter)_module .*)$/\1/' \
    /usr/local/apache2/conf/httpd.conf \
    && printf '\nInclude conf/extra/japandi.conf\n' \
    >> /usr/local/apache2/conf/httpd.conf

COPY docker/apache.conf /usr/local/apache2/conf/extra/japandi.conf

COPY index.html privacy.html 404.html robots.txt sitemap.xml .htaccess /usr/local/apache2/htdocs/
COPY assets/ /usr/local/apache2/htdocs/assets/
COPY id/ /usr/local/apache2/htdocs/id/
COPY projects/ /usr/local/apache2/htdocs/projects/

RUN httpd -t
