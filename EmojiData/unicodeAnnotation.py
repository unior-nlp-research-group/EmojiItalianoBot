# coding=utf-8

import requests
import json

def processAnnotationFromUrl(language_code):
    from xml.etree import ElementTree
    from collections import defaultdict
    ANNOTATION_URL = 'https://raw.githubusercontent.com/unicode-org/cldr/master/common/annotations/'
    # ANNOTATION_DERIVED_URL = 'http://unicode.org/repos/cldr/trunk/common/annotationsDerived/'
    annotation_dict = defaultdict(list)
    for base_url in [ANNOTATION_URL]: # [ANNOTATION_URL, ANNOTATION_DERIVED_URL]:
        url = base_url + '{}.xml'.format(language_code)
        print 'parsing {}'.format(url)
        #response = requests.get(url, stream=True)
        #response.raw.decode_content = True
        response = requests.get(url)
        root = ElementTree.fromstring(response.content)
        for annotation in root.iter('annotation'):
            emoji = annotation.attrib['cp']
            annotation_entries = [a.strip()
                                  for a in annotation.text.split('|')]
            entry_list = annotation_dict[emoji]
            for anno in annotation_entries:
                if anno not in entry_list:
                    entry_list.append(anno)
    return annotation_dict

def update_annotations():
    import codecs    
    file_data = {
        'it': 'emoji_tags_it.json',
        'en': 'emoji_tags_en.json',
    }
    for lang, file_in in file_data.items():
        with codecs.open(file_in, 'w', encoding='utf-8') as f_out:
            d = processAnnotationFromUrl(lang)
            json.dump(d, f_out, indent=4, sort_keys=True, ensure_ascii=False)

if __name__ == "__main__":
    update_annotations()