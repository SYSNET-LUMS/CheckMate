#include <stddef.h>
#include <string.h>
#include <limits.h>
#include <search.h>

#ifndef LOCAL_RUN
#include "support/msp430-support.h"
#endif

// #include "../bareBench.h"

static size_t table[UCHAR_MAX + 1];
static size_t len;
static char *findme;

/*
**  Call this with the string to locate to initialize the table
*/

void init_search(const char *string)
{
      size_t i;

      len = strlen(string);
      for (i = 0; i <= UCHAR_MAX; i++) /* rdg 10/93 */
            table[i] = len;
      for (i = 0; i < len; i++)
            table[(unsigned char)string[i]] = len - i - 1;
      findme = (char *)string;
}

/*
**  Call this with a buffer to search
*/

#include <string.h>

char *strsearch(const char *string) {
    size_t pos = len - 1; // Start position at the end of the substring
    size_t limit = strlen(string);

    while (pos < limit) {
        // Get shift value
        size_t shift = table[(unsigned char)string[pos]];

        if (shift == 0) {
            // If shift is zero, attempt to compare the strings
            char *here = (char *)&string[pos - len + 1];
            if (strncmp(findme, here, len) == 0) {
                return here; // Match found
            }
            pos++; // Increment pos to avoid infinite loop
        } else {
            // Apply shift
            pos += shift;
        }
    }

    return NULL; // No match found
}


#include <stdio.h>

int main()
{
      char *here;
      char *find_strings[] = {"Kur",
                              "gent",
                              "lass",
                              "suns",
                              "for",
                              "xxx",
                              "long",
                              "have",
                              "where",
                              "xxxxxx",
                              "xxxxxx",
                              "pense",
                              "pow",
                              "xxxxx",
                              "Yo",
                              "and",
                              "faded",
                              "20",
                              "you",
                              "bac",
                              "an",
                              "way",
                              "possibili",
                              "an",
                              "fat",
                              "imag",
                              "th",
                              "wor",
                              "xxx",
                              "xxx",
                              "yo",
                              "bxx",
                              "wo",
                              "kind",
                              "4",
                              "idle",
                              "Do",
                              "scare",
                              "people",
                              "wit",
                              "xxx",
                              "xxx",
                              "Th",
                              "xxx",
                              "yourself",
                              "Forget",
                              "succeed",
                              "Kee",
                              "lov",
                              "yo",
                              "Stretc",
                              "what",
                              "life",
                              "kno",
                              "wha",
                              "xxx",
                              "xxx",
                              "40",
                              "Get",
                              "xxx",
                              "them",
                              "Maybe",
                              "may",
                              "you",
                              "the",
                              "your",
                              "congratulate",
                              "much",
                              "either",
                              "are",
                              "Enjoy",
                              "it",
                              "be",
                              "other",
                              "it",
                              "xxx",
                              "greatest",
                              "own",
                              "nowhere",
                              "room",
                              "you",
                              "beauty",
                              "feel",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "xxx",
                              "it",
                              "Northern",
                              "before",
                              "Accept",
                              NULL};
      char *search_strings[] = {"Kurt Vonneguts Commencement Address at",
                                "MIT Ladies and gentlemen of",
                                "the class of 97 Wear",
                                "sunscreen If I could offer",
                                "you only one tip for",
                                "the future sunscreen would be",
                                "it The longterm benefits of",
                                "sunscreen have been proved by",
                                "scientists whereas the rest of",
                                "my advice has no basis",
                                "more reliable than my own meandering experience",
                                "I will dispense this advice",
                                "now Enjoy the power and beauty",
                                "of your youth Oh never mind",
                                "You will not understand the power",
                                "and beauty of your youth until theyve",
                                "faded But trust me in",
                                "20 years",
                                "youll look",
                                "back at photos of yourself",
                                "and recall in a",
                                "way you cant grasp now how much",
                                "possibility lay before you",
                                "and how fabulous you really looked You",
                                "are not as fat",
                                "as you imagine Dont worry about",
                                "the future Or",
                                "worry but know that worrying is as effective",
                                "as trying to solve an algebra equation",
                                "by chewing bubble gum The real troubles in",
                                "your life are apt to",
                                "be things that never crossed your",
                                "worried mind the",
                                "kind that blindside you at",
                                "4 pm on some",
                                "idle Tuesday",
                                "Do one thing every day that",
                                "scares you Sing Dont be reckless with other",
                                "peoples hearts Dont put up",
                                "with people who are reckless",
                                "with yours Floss Dont waste your time",
                                "on jealousy Sometimes youre ahead sometimes youre behind",
                                "The race is long and in",
                                "the end its only with",
                                "yourself Remember compliments you receive",
                                "Forget the insults If you",
                                "succeed in doing this tell me how",
                                "Keep your old",
                                "love letters Throw away",
                                "your old bank statements",
                                "Stretch Dont feel guilty if you dont know",
                                "what you want to do with your",
                                "life The most interesting people I",
                                "know didnt know at 22",
                                "what they wanted",
                                "to do with their lives Some of",
                                "the most interesting",
                                "40yearolds I know still dont",
                                "Get plenty of calcium",
                                "Be kind to your knees Youll miss",
                                "them when theyre gone",
                                "Maybe youll marry",
                                "maybe you wont Maybe youll have children maybe",
                                "you wont Maybe youll divorce at 40 maybe youll dance",
                                "the funky chicken on",
                                "your 75th wedding anniversary Whatever",
                                "you do dont congratulate yourself too",
                                "much or berate yourself",
                                "either Your choices are half chance So",
                                "are everybody elses",
                                "Enjoy your body Use",
                                "it every way you can Dont",
                                "be afraid of it or of what",
                                "other people think of",
                                "it Its",
                                "the",
                                "greatest instrument youll ever",
                                "own Dance even if you have",
                                "nowhere to do it but your living",
                                "room Read the directions even if",
                                "you dont follow them Do not read",
                                "beauty magazines They will only make you",
                                "feel ugly Get to know your parents You never",
                                "know when theyll be gone for good Be",
                                "nice to your siblings Theyre your",
                                "best link to your",
                                "past and the people most likely",
                                "to stick with you",
                                "in the future Understand that",
                                "friends come and go but",
                                "with a precious few you should hold",
                                "on Work hard to bridge",
                                "the gaps in geography and lifestyle",
                                "because the older",
                                "you get the more you need the",
                                "people who knew you when you",
                                "were young Live",
                                "in New York City once but leave before",
                                "it makes you hard Live in",
                                "Northern California once but leave",
                                "before it makes you soft Travel",
                                "Accept certain inalienable truths Prices will rise",
                                "Politicians will philander You too will",
                                "worth But trust me on the sunscreen"};
      int i;
      int y;
      int sum = 0;

      for (y = 0; y < 100; ++y)
      {
            for (i = 0; i < 100; i++)
            {
                  init_search(find_strings[y]);
                  here = strsearch(search_strings[i]);
#ifdef LOCAL_RUN
printf("%d\n", here ? 1 : 0);
here ? sum++: (void)0;
#endif
                  // printf("\"%s\" is%s in \"%s\"", find_strings[i],
                  //       here ? "" : " not", search_strings[i]);
                  // if (here)
                  //       printf(" [\"%s\"]", here);
                  // printf("\n");
            }
      }
#ifdef LOCAL_RUN
      printf("%d",sum);
#else
      indicate_end();
#endif
      return 0;
}