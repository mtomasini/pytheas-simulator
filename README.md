# Pytheas - a flexible and agile simulator of ancient seafaring

Current research in the [Maritime Encounters project](https://www.gu.se/en/research/maritime-encounters), at the University of Gothenburg, has been led by using and developing the software [Voyager](https://github.com/mtomasini/voyager). While this software is very complete and thorough, it can be difficult to maintain and develop due to the many components that it uses. I decided to write a version of the code that is more flexible and less complex to use, based on my own experiences in simulating seafaring in ancient times. This software is an improvement on the work by Alvaro Montenegro (Ohio State University) and Victor Wåhlstrand Skärström (University of Gothenburg, now at Chalmers University of Technology). The code is written in Python.

At this stage, I only make available the code [and its documentation](https://mtomasini.github.io/pytheas-simulator/); at a latter stage, I will make available:

- [ ] A demonstration file with attached parameters
- [ ] A complete vignette containing a description of all functionalities
- [ ] A script to download data from Copernicus for usage within Pytheas
- [ ] (Optional) A snakemake file or similar that will help the user picking a few parameters and simulating with Pytheas without having to download data locally.

## Development philosophy

The code for Voyager was documented but had no tests. In the development of this new software, it is my intention to have even better documentation as well as unit testing. This follows from years of working in an academic context where tests are an afterthought and are seldom developed. But when using a software developed over years, by developers who have since quit the workplace, and that has required quick developments to respond to publication deadlines, the lack of testing in particular has proven deleterious, leading to bad mistakes at the production stage.

## Name of the software

I decided to name this new iteration of the Voyager software "Pytheas". Pytheas was an ancient Greek navigator from Massalia (modern Marseille) who in around 330 BCE went on a sailing travel to the far North of Europe, reaching the British Isles and travelling further north to _Ultima Thule_ (which may be, according to Barry Cunliffe[^1], most probably Iceland, but possibly Norway or Shetland).

## License

This software is packaged with a MIT License.

[^1]: The Extraordinary Voyage of Pytheas the Greek, Barry Cunliffe (2001), Chapter 6.
