#!/usr/bin/env python

import os.path
import pathlib
import CommonMark
import yaml
from jinja2 import Environment, FileSystemLoader

PAGES_DIR = "pages"
TEMPLATE_DIR = "templates"
DEFAULT_DEST = "build"
FRONT_MATTER_DELIMITER = "---\n"
DEFAULT_TEMPLATE = "default.html"


class WipyPageNotFoundError(Exception):
    pass


class ReadOnlyDict(dict):

    def __setitem__(self, key, value):
        raise TypeError("This dictionary is read only")

    def __delitem__(self, key):
        raise TypeError("This dictionary is read only")



class WipyDictIndex():
    def __init__(self, repository):
        self.repository = repository

    def __getitem__(self, key):
        filename = str(pathlib.Path(
            self.repository.config['wiki-root']).joinpath(key + '.md'))

        try:
            document = WipyDocument(filename)
        except IOError:
            raise WipyPageNotFoundError('Page ' + key + ' not found.')

        return document.dictionary


    
class WipyPagesIndex(WipyDictIndex):

    def __init__(self, repository):
        self.repository = repository

    def __getitem__(self, key):
        dictionary = super().__getitem__(key)
        
        if 'template' in dictionary:
            templateName = dictionary['template']
        else:
            templateName = self.repository.config['default-template']
        template = self.repository.templateEnvironment.get_template(
            templateName)

        return template.render(dictionary)


    
class WipyRepository:
    """ Models a whole repository of wipy articles, along with templates and the
    www-root and so on.

    """

    def __init__(self, configFilePath):
        # Load defaults in the config.
        config = {'www-root': '/var/www',
                  'wiki-root': '/var/wiki',
                  'template-directory': '/var/www/template',
                  'default-template': 'default.html'}

        try:
            f = open(configFilePath, 'r')
        except IOError:
            print("Config file not found.")

        config.update(yaml.safe_load(f))
        self.config = ReadOnlyDict(config)
        self.templateEnvironment = Environment(
            loader=FileSystemLoader(self.config['template-directory']))

        self.pages = WipyPagesIndex(self)
        self.dictionaries = WipyDictIndex(self)

    def update(self, pageName, newText):
        fullPath = pathlib.Path(
            self.config['wiki-root']).joinpath(pageName + '.md')
        print('Updating ' + str(fullPath) + '.')
        try:
            f = open(str(fullPath), 'w')
        except IOError:
            print('Could not open the file to be updated')
            raise

        f.write(newText)
        f.truncate()
        f.close()
        print('Wrote it!')


class WipyDocument:
    """ """

    def __init__(self, filename):

        tail = pathlib.Path(filename).name
        self._dictionary = {'template': DEFAULT_TEMPLATE, 'filename': tail, 'path': '/w/' + tail.split('.')[0]}

        try:
            f = open(filename, 'r')
        except IOError:
            print('Wipy document "%s" not found', filename)
            raise

        self._dictionary['raw'] = f.read()
        f.seek(0)

        frontMatterString = self.extractFrontMatter(f)
        frontMatter = yaml.load(frontMatterString)

        if frontMatter:
            self._dictionary.update(frontMatter)
        
        mdPartOfDocument = f.read()
        f.close()

        self._dictionary['content'] = self.parseMarkdown(mdPartOfDocument)

    def parseMarkdown(self, f):
        parser = CommonMark.DocParser()
        renderer = CommonMark.HTMLRenderer()

        # Ast stands for Abstract Syntax Tree.
        ast = parser.parse(f)
        return renderer.render(ast)

    def extractFrontMatter(self, f):
        """ Reads only the yaml front matter on a wiki page. """

        frontMatter = ""
        if f.readline() == '---\n':
            lineBuffer = f.readline()
            while lineBuffer != FRONT_MATTER_DELIMITER and lineBuffer != "":
                frontMatter += lineBuffer
                lineBuffer = f.readline()

        return frontMatter

    @property
    def dictionary(self):
        return self._dictionary

    @dictionary.setter
    def dictionary(self, rhs):
        self._dictionary = rhs

    def render(self, templateDir):
        env = Environment(loader=FileSystemLoader(templateDir))
        template = env.get_template(self.template)
        dico = self.dictionary()
        return template.render(dico)


def buildPage(inputFilename, outputFilename):
    pass


def build(src, dest=None, force=False):
    pathToPages = os.path.join(src, PAGES_DIR)

    env = Environment(loader=FileSystemLoader(os.path.join(src, TEMPLATE_DIR)))

    destPath = None
    if dest is None:
        destPath = os.path.join(src, DEFAULT_DEST)
    else:
        destPath = dest

    for page in filter(lambda x: x.endswith(".md"), os.listdir(pathToPages)):
        print(page)
        document = WipyDocument(os.path.join(pathToPages, page))
        template = env.get_template('default.html')
        output = template.render(document.dictionary())
        f = open(os.path.join(destPath, page[:-3] + ".html"), 'w')
        print(os.path.join(destPath, page[:-3] + ".html"))
        f.write(output)
        f.close()

if __name__ == '__main__':
    print('Hello world!')
