#!/usr/bin/env python

import os
import sys
import json
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader("platforms"),
    extensions=['jinja2.ext.autoescape'],
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=True)

schema_path = sys.argv[1]
prefix = sys.argv[2]
package = sys.argv[3]

schema = json.load(open(schema_path))

def generate(platform, name, definition):
	name = name[:1].upper() + name[1:]
	print "Generating %s %s ..." % (platform, name)

	for template_file in os.listdir('platforms/' + platform + '/object'):
		# ['object/definition.h', 'object/implementation.m']:
		template = JINJA_ENVIRONMENT.get_template(platform + '/object/' + template_file)

		properties = definition.get('properties', {})
		for _, property in properties.iteritems():
			if property.get("$ref"):
				type, = property.get("$ref").split('/')[-1:]
				property['type'] = type

		result = template.render({
			'prefix': prefix,
			'package': package,
			'name': name,
			'properties': properties
		})

		folder = 'output/' + platform
		if platform == 'android':
			folder = folder  + '/' + '/'.join(package.split('.'))

		if not os.path.exists(folder):
			os.makedirs(folder)

		_, ext = os.path.splitext(template_file)
		with open(folder + '/' + (prefix if platform == 'ios' else '') + name + ext, 'w') as file:
			file.write(result)


for platform in ['ios', 'android']:
	name = schema.get('title').split()[0]
	generate(platform, name, schema)
	for name, definition in schema.get('definitions', {}).iteritems():
		if definition['type'] == 'object':
			generate(platform, name, definition)


