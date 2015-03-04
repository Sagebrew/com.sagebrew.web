# How do I format my questions and solutions using Markdown? #
Technically speaking Markdown is a formatting language that produces plain 
text that can be easily converted to HTML. What that means is, Markdown is a 
writing system that allows easy customization of plain text, specifically 
including headers, ordered lists, block quotations, bold and italics, 
links etc. With Markdown it becomes very simple to write up Questions and 
Solutions, providing Context, citing sources and organizing the information 
you wish to present.

## The Specifics ##
### Headers ###
Headers are indicated by hash tags. For example:

    # Header #

will translate to:
# Header #

The number of hash tags preceding a header will determine the size of the 
header. Six `#` symbols is the smallest Header. Any more than 6 `#` symbols 
and the text will remain the same.

A full list of header examples can be found below:


    # Header One #
    ## Header Two ##
    ### Header Three ###
    #### Header Four ####
    ##### Header Five #####
    ###### Header Six ######


The render to the following respectively:
# Header One #
## Header Two ##
### Header Three ###
#### Header Four ####
##### Header Five #####
###### Header Six ######



 
### Ordered Lists ###
To make an ordered list, simply use the dash, or `-` key. For example: 

    - list one
    - list two  
    - list three

will translate to

- list one
- list two
- list three

To nest the list, use 4 spaces before the `-` symbol you put in front of a line. 
For example:


    - list one
        - list two

will translate to

- list one
    - list two


Ordered Lists are a great way to organize thoughts and ideas.  


### Adding Links ###
To add a link, simply place the word or words you'd like linked in brackets
(it's best to link a word or two). Then, at the bottom of your page, 
define your link. For example: 


    This is a [link]. 
    
    ... Some Content ...
    
    [link]: https://www.google.com 

will tranlaste to 

This is a [link]. 


This will let the text editor know that your bracketed [link] will take you to 
the designated web address. You may also use numbers to designate links. 
For example:


    This is a [link][1]
    
    ... Some Content ...
    
    [1]: https://www.google.com 

will translate to

This is a [link][1]

This is a great method for citing sources within the Context of a Question or
a Solution. 

Block Quotes
To add block quotes to your text, use the right-facing arrow key, `>` to 
indicate that a line of text should be a block quote. For Example

    >this is what block quotes would look like
    >when arranged in Markdown formatting. 
    >It's really not difficult at all! 

would translate to

>this is what block quotes would look like
> when arranged in Markdown formatting.
> It's really not difficult at all!

So, by simply placing a `>` before a line of text, you get nice, 
neat block quotes! This becomes helpful when quoting text or speech, 
especially when citing one of your research studies or journal articles. 

### Images ###
To add Images, put an exclamation point `!` before brackets containing an 
image description, and a number for reference in separate brackets.
Then, at the bottom of your page, define your image by the number
For example:

    ![This is a picture][2]
    
    ... Some Content ...
    
    [2]: https://s3.amazonaws.com/sagebrew/10984046_596208397180366_3248774050269017847_n.jpg

would translate to:

![This is a picture][2]

This will let the editor know which image to use, and where. 
Our editor will automatically resize your image to fit neatly on the page if it
is too large, but if you can resize your image, it's recommended to do so.
Preferred image size is at or below 750x500.

### Videos ###


For example:

    <iframe src="https://player.vimeo.com/video/120960412" width="500" height="281" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe> <small><a href="https://vimeo.com/120960412">Baxter</a> from <a href="https://vimeo.com/tcoyle">Ty Coyle</a> on <a href="https://vimeo.com">Vimeo</a>.</small>

would translate to:

<iframe src="https://player.vimeo.com/video/120960412" width="500" height="281" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe> <small><a href="https://vimeo.com/120960412">Baxter</a> from <a href="https://vimeo.com/tcoyle">Ty Coyle</a> on <a href="https://vimeo.com">Vimeo</a>.</small>


### Preformatted Text ###
To add preformatted text, simply indent your desired text 4 spaces. This will 
place your text in a special block that retains 
formatting such as  spacing and indentation. Basically, your text will 
look exactly as you write it (Please note that copying and pasting in text from
something like Word will not maintain its formatting due to Word's proprietary 
formatting). An example of this formatting is as follows:

    Here is some formatted text
         that will translate exactly how you write it

This can be helpful when trying to specifically format something in Markdown 
that the editor doesn't easily allow, such as preserving extra spaces or 
line breaks.

The other solution for adding preformatted text is to surround your text with
``` ` ```. This will result in an inline preformatting which doesn't handle spacing
but does allow for you to specific pieces of text you don't want the markdown
editor to interpret. For example:

    `#### This shouldn't be a header ####`

would translate to `#### This shouldn't be a header ####` rather than:

#### This shouldn't be a header ####

**NOTE:** You must leave a blank line between your previous, non-formatted, text 
and your preformatted text if you are using the 4 spaces rather than ``` ` ```.


### Italics ###
To make Italics, simply surround the words you want italicized with `*`. 
For example:

    *Hello, this is italicized. Isn't that a neat word? Italicized.*

becomes

*Hello, this is italicized. Isn't that a neat word? Italicized.* 

### Bold ###
To make text Bold, simply surround the words you want to be bold with two `*`.
For example:


    **This text, on the other hand, is now bold.**

becomes

**This text, on the other hand, is now bold.**

These are basic Markdown commands and how they translate to plain text 
formatting. Give it a try in the Markdown Practice Box below!


[link]: https://www.google.com 
[1]: https://www.google.com 
[2]: https://s3.amazonaws.com/sagebrew/10984046_596208397180366_3248774050269017847_n.jpg
[3]: https://vimeo.com/channels/staffpicks/120960412