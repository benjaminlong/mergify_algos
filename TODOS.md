# TODOS

- Check coverage
- Create Sphinx Documentation
- Improve UTs
- Improve Comments


## Known Issues

- On large GitHub project with many stargazers, project will have issues to
return information.

So our Algorithm limit the amount of data we retry from Github.
See our API documentation to understand how you can control it.

- Algo using GraphQl API doesn't work on large project. GitHub always return
errors.

## Improvements

- Use Async Task? If we want valuable information on medium/large project, 
the algorithm will eventually take several minutes to complete.
- On very large project, we will eventually reach memory limitation.
- Cache Repository information
- Cache User's starred repositories information
