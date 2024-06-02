import os
import random
import re
import sys
from collections import Counter

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
    distribution = {}
    if not corpus[page]:
        equal = 1 / len(corpus)
        for key in corpus:
            distribution[key] = equal
    else:
        df_probability = (1 - damping_factor) / len(corpus)
        probability = damping_factor / len(corpus[page])
        for key in corpus:
            if key in corpus[page]:
                distribution[key] = probability + df_probability
            else:
                distribution[key] = df_probability
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    choice = random.choice(list(corpus))
    counter = []
    for _ in range(n):
        counter.append(choice)
        distribution = transition_model(corpus, choice, damping_factor)
        population = list(distribution.keys())
        weights = list(distribution.values())
        choice = random.choices(population, weights)[0]

    tally = dict(Counter(counter))
    for key in tally:
        tally[key] = tally[key] / n

    return tally


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pr = {}
    new_pr = {}
    for key in corpus:
        if not corpus[key]:
            corpus[key] = set(corpus)
        pr[key] = 1 / N

    while True:
        difference = []
        for p in pr:
            summa = 0
            for i in corpus:
                if p in corpus[i]:
                    summa += pr[i] / len(corpus[i])
            new_pr[p] = round(((1 - damping_factor) / N) + (damping_factor * summa), 5)
        for key in pr:
            difference.append(abs(pr[p] - new_pr[p]))
            pr[key] = new_pr[key]
        if max(difference) <= 0.001:
            return pr


if __name__ == "__main__":
    main()
