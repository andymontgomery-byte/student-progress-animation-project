student progress animation

- Given the raw MAP data xlsx files - I'll be dropping in new ones periodically as the more test scores come in.
- and the MAP norms tables - I have the 2020 ones right now, but the 2025 ones that we want to use aren't available yet.
  - the 2020 normstables.pdf is too big. if you read it into context you will crash, so break it up into smaller context safe pieces before you read them into context.
  - write test cases for the extraction, so you can prove that all the tables were extracted correctly for all seasons, all subjects, all percentiles, and all grade levels.
- Build a table with the following:
  - student email
  - grade level
  - campus - it is called school
  - subject - it is called course
  - Starting percentile - testpercentile when the term is fall of this school year
    - 99th grade levels
  - Current percentile - testpercentile when the term is winter of this year
    - 99th grade levels
  - Projected end of year percentile (using same point gain as fall to winter) - point gain is falltowinterobservedgrowth.  in the nwea norms tables, look  up the percentile associated with the RIT score adding falltowinterobserved growth to the winter term testritscore.
    - 99th grade levels
  - 99th percentile grade levels - these columns are added after each of the percentile columns to help differentiate different levels of being 99th percentile.  indicates the number of grade levels beyond their current grade level their RIT score says they are 99th percentile for.  for example,  a 99th percentile 4th grader whose RIT score says they are also 99th percentile at 5th and 6th grade would have a 2 in this column.
  - conditional growth index - this is the number of standard deviations above the norm of the student's growth.  0 means growth was typical.  1 means the student growth was 1 standard deviation above the norm
- once we have the table, we will filter for student / subject combinations above .8 std deviations.  How many student subject combinations are there? How many student subject combinations total?
- then we will build a web app, where you can select a student subject combination, and show a simple growth animation with percentile 0-99 augmented by 99th grade levels on the Y-axis and fall, winter, spring on the X axis.

## Future Analysis
- Try thread scores
- Do fast math analysis - who did fast math and who did well
