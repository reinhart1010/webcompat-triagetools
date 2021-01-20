import sys
import re
from consolemenu import *
from consolemenu.items import *

from http import client
import requests
import tldextract
import urllib.parse
from xml.dom.minidom import parse
import xml.dom.minidom

contact_text_list = ["contact", "about", "kontakt", "kontakta", "kontak", "hubungi"]
url_blocklist = ["blog", "post", "thread", "features"]


def exists(string, arr):
    for i in arr:
        if i in string:
            return True
    return False


# Define the main menu
def main():
    main_menu = ConsoleMenu("Webcompat Triage Tools")

    main_menu.append_item(FunctionItem("Find the site's Contact information", find_contact_init))
    main_menu.show()


def find_contact_init():
    print("Enter the URL to be searched:")
    url = input(sys.stdin)

    # Extract the main url
    domain_info = tldextract.extract(url)

    # Try getting the sitemaps
    print("Attempt 1: Get the sitemap")
    if (domain_info.subdomain):
        sitemap_domain = domain_info.subdomain + "." + domain_info.domain + "." + domain_info.suffix
    else:
        sitemap_domain = domain_info.domain + "." + domain_info.suffix

    sitemap_domain_alt = domain_info.domain + "." + domain_info.suffix

    sitemap_url = ["http://" + sitemap_domain + "/robots.txt"]

    i = 0
    j = 1

    k = 0

    while (i < j):
        if (i > 0):
            # Extract the main url
            domain_info = tldextract.extract(url)

        print("[INFO] GET", sitemap_url[i])
        sitemap_res = requests.get(sitemap_url[i])
        if (sitemap_res.status_code == 200):
            if (i == 0):
                # Robots.txt file
                robots_txt_dump = sitemap_res.text.splitlines()
                for line in robots_txt_dump:
                    temp = line.split()
                    if (len(temp) == 0):
                        continue
                    if (temp[0]) == "Sitemap:":
                        print("Found additional sitemap:", temp[1])
                        sitemap_url.append(temp[1])
                        j += 1
            else:
                # Sitemap.xml file
                sitemap_raw = sitemap_res.text

                try:
                    sitemap_dom = xml.dom.minidom.parseString(sitemap_raw).documentElement
                    additional_sitemaps = sitemap_dom.getElementsByTagName("sitemap")
                    additional_links = sitemap_dom.getElementsByTagName("url")

                    for links in additional_links:
                        for links_child in links.childNodes:
                            if links_child.localName == "loc":
                                if exists(links_child.childNodes[0].data, contact_text_list):
                                    print("Possible Contact page:", links_child.childNodes[0].data)
                                    k += 1
                                if not exists(links_child.childNodes[0].data, url_blocklist):
                                    if domain_info.domain != "github" and "github" in links_child.childNodes[0].data:
                                        print("Possible GitHub page:", links_child.childNodes[0].data)
                                        k += 1
                                    elif domain_info.domain != "twitter" and "twitter" in links_child.childNodes[0].data:
                                        print("Possible Twitter page:", links_child.childNodes[0].data)
                                        k += 1
                                    elif "email" in links_child.childNodes[0].data:
                                        print("Possible Email page:", links_child.childNodes[0].data)
                                        k += 1
                                    elif "help" in links_child.childNodes[0].data:
                                        print("Possible Help page:", links_child.childNodes[0].data)
                                        k += 1
                                    elif "faq" in links_child.childNodes[0].data:
                                        print("Possible FAQ page:", links_child.childNodes[0].data)
                                        k += 1

                    for sitemap in additional_sitemaps:
                        for sitemap_child in sitemap.childNodes:
                            if sitemap_child.localName == "loc":
                                # print("Found additional sitemap:", sitemap_child.childNodes[0].data)
                                sitemap_url.append(sitemap_child.childNodes[0].data)
                                j += 1
                except xml.parsers.expat.ExpatError:
                    print("Parser error")
                    pass

        i += 1
        print("[INFO] Searched", i, "out of", j, "sitemaps")
        if (j == 1):
            # Add more possible sitemap.xml locations
            print("[INFO] The site's robots.txt does not include any sitemap")
            print("[INFO] Searching for possible sitemap locations")
            j += 8
            sitemap_url.append("http://" + sitemap_domain + "/sitemap.xml")
            sitemap_url.append("http://" + sitemap_domain + "/sitemap-index.xml")
            sitemap_url.append("http://" + sitemap_domain + "/sitemap_index.xml")
            sitemap_url.append("http://" + sitemap_domain + "/.sitemap.xml")
            sitemap_url.append("http://" + sitemap_domain + "/sitemap")
            sitemap_url.append("http://" + sitemap_domain + "/sitemap/sitemap-index.xml")
            sitemap_url.append("http://" + sitemap_domain + "/sitemap/sitemap_index.xml")
            sitemap_url.append("http://" + sitemap_domain + "/admin/config/search/xmlsitemap")
        elif (k > 10):
            print("[INFO] Maximum limit of 10 links has been reached. Stopping...")
            j = 0
        elif (i == j and sitemap_domain != sitemap_domain_alt and not sitemap_domain.startswith("www.")):
            i = 0
            j = 1
            sitemap_domain = sitemap_domain_alt
            sitemap_url = ["http://" + sitemap_domain + "/robots.txt"]



    # if domain_info.subdomain:
    #     sitemap_url = "http://" + domain_info.subdomain + "." + domain_info.domain + "." + domain_info.suffix
    # else:
    #     sitemap_url = "http://" + domain_info.domain + "." + domain_info.suffix
    #
    # sitemap_tree = sitemap_tree_for_homepage(sitemap_url)
    # for page in sitemap_tree.all_pages():
    #     if page.news_story is None:
    #         if exists(page.url.lower(), contact_text_list):
    #             print("Possible Contact page:", page.url)
    #         if not exists(page.url.lower(), url_blocklist):
    #             if domain_info.domain != "github" and "github" in page.url.lower():
    #                 print("Possible GitHub page:", page.url)
    #             elif domain_info.domain != "twitter" and "twitter" in page.url.lower():
    #                 print("Possible Twitter page:", page.url)
    #             elif "email" in page.url.lower():
    #                 print("Possible Email page:", page.url)
    #             elif "help" in page.url.lower():
    #                 print("Possible Help page:", page.url)
    #             elif "faq" in page.url.lower():
    #                 print("Possible Help page:", page.url)


main()