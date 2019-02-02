"""
Created by adam on 10/18/18
"""
__author__ = 'adam'

import seaborn as sns
import wordcloud
from matplotlib import pyplot as plt

sns.set( style="whitegrid" )


def draw_cloud( wordlist, title, font_size=20 ):
    """Given a list of words, it plots a wordcloud"""
    # make into block of text
    words = ' '.join( wordlist )

    wc = wordcloud.WordCloud(
        width=2500,
        height=2000
    ).generate( words )
    plt.figure( 1, figsize=(13, 13) )
    plt.imshow( wc )
    plt.axis( 'off' )
    plt.title( title )
    ax = plt.gca()
    ax.title.set_fontsize( font_size )
    plt.show()


def draw_cloud_from_freqs( freqs, week_num, title, font_size=20 ):
    """Given the frequency object with keys like w1, w2,
    this plots a wordcloud from those frequencies
    """
    f = { }
    w = "w%s" % week_num
    for k in freqs[ w ].freqDist:
        f[ k ] = freqs[ w ].freqDist.freq( k )

    wc = wordcloud.WordCloud( width=2500, height=2000 ).generate_from_frequencies( f )
    plt.figure( 1, figsize=(13, 13) )
    plt.imshow( wc )
    plt.axis( 'off' )
    plt.title( title )
    ax = plt.gca()
    ax.title.set_fontsize( font_size )
    plt.show()


def draw_cumulative_freq( freqs, week_num, max_terms=30, font_size=20 ):
    """Plots cumulative frequencies of terms"""
    week = "w%s" % week_num

    fig = plt.gcf()
    ax = plt.gca()
    ax.set_title( week )

    #     # rotate the x axis labels to 45 degrees
    #     for tick in ax.get_xticklabels():
    #         tick.set_rotation(45)

    fig.set_figwidth( 13 )
    fig.set_figheight( 5 )
    # change the font size
    for item in ([ ax.title, ax.xaxis.label, ax.yaxis.label ] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize( font_size )

    plt.xticks( rotation=45 )

    freqs[ week ].plot( max_terms )
    fig.tight_layout()


if __name__ == '__main__':
    pass
