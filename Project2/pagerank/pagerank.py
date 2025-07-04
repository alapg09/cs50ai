import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    result = {}
    links = corpus[page]
    num_pages = len(corpus)
    num_links = len(links)

    if(links):

        for key in corpus:
            result[key] = (1 - damping_factor) / num_pages
        
        for key in links:
            result[key] += damping_factor / num_links
    
    else:
        for key in corpus:
            result[key] = 1.0 / num_pages

    return result

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    result = {}
    for page in corpus:
        result[page] = 0
    
    page = random.choice(list(corpus.keys()))

    for i in range(n):
        result[page] += 1

        model = transition_model(corpus, page, damping_factor)

        links = list(model.keys())
        probabilities = list(model.values())
        page = random.choices(links, probabilities)[0]

    pagerank = {}

    for key in result:
        pagerank[key] = result[key] / n

    sum = 0
    for i in pagerank:
        sum += pagerank[i]

    return pagerank
        
    
def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    result = {}
    num_pages = len(corpus)
    for key in corpus:
        result[key] = 1 / num_pages

    new_ranks = result.copy()

    while True:
        for page in corpus:
            total = (1 - damping_factor) / num_pages

            for p in corpus:
                if page in corpus[p]:
                    total += damping_factor * (result[p] / len(corpus[p]))
                if not corpus[p]:
                    total += damping_factor * (result[p] / num_pages)

            new_ranks[page] = total

        converged = True
        for p in result:
            diff = abs(new_ranks[p] - result[p])
            if diff >= 0.001:
                converged = False
                break
        if converged == True:
            break
        else:
            result = new_ranks.copy()
    
    return new_ranks


if __name__ == "__main__":
    main()
