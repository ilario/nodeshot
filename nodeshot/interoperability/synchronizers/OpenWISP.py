import simplejson as json
from dateutil import parser

from django.template.defaultfilters import slugify
from django.contrib.gis.geos import Point

from nodeshot.core.nodes.models import Node
from nodeshot.core.nodes.models.choices import NODE_STATUS

from .base import XMLConverter


class OpenWISP(XMLConverter):
    """ OpenWISP GeoRSS interoperability class """
    
    def save(self):
        """ synchronize DB """
        # retrieve all items
        items = self.parsed_data.getElementsByTagName('item')
        
        # init empty lists
        added_nodes = []
        changed_nodes = []
        unmodified_nodes = []
        
        # retrieve a list of local nodes in DB
        local_nodes_slug = Node.objects.filter(layer=self.layer).values_list('slug', flat=True)
        # init empty list of slug of external nodes that will be needed to perform delete operations
        external_nodes_slug = []
        deleted_nodes_count = 0
        
        # loop over every parsed item
        for item in items:
            # retrieve info in auxiliary variables
            # readability counts!
            guid = self.get_text(item, 'guid')
            name, created_at = guid.split('201', 1)
            slug = slugify(name)
            created_at = "201%s" % created_at
            updated_at = self.get_text(item, 'updated')            
            lat, lng = self.get_text(item, 'georss:point').split(' ')
            description = self.get_text(item, 'title')
            address = self.get_text(item, 'description')
            
            # point object
            point = Point(float(lng), float(lat))
            
            # convert dates to python datetime
            created_at = parser.parse(created_at)
            updated_at = parser.parse(updated_at)
            
            # default values
            added = False
            changed = False
            
            try:
                # edit existing node
                node = Node.objects.get(slug=slug)
            except Node.DoesNotExist:
                # add a new node
                node = Node()
                node.layer = self.layer
                node.status = NODE_STATUS.get('active')  # TODO: solve status debate...
                added = True
            
            if node.name != name:
                node.name = name
                changed = True
            
            if node.slug != slug:
                node.slug = slug
                changed = True
            
            if added is True or node.coords.equals(point) is False:
                node.coords = point
                changed = True
            
            if node.description != description:
                node.description = description
                changed = True
            
            if node.address != address:
                node.address = address
                changed = True
            
            if node.added != created_at:
                node.added = created_at
                changed = True
            
            if node.updated != updated_at:
                node.updated = updated_at
                changed = True
            
            if added or changed:
                node.full_clean()
                node.save(auto_update=False)
            
            if added:
                added_nodes.append(node)
                self.verbose('new node saved with name "%s"' % node.name)
            elif changed:
                changed_nodes.append(node)
                self.verbose('node "%s" updated' % node.name)
            else:
                unmodified_nodes.append(node)
                self.verbose('node "%s" unmodified' % node.name)
            
            # fill node list container
            external_nodes_slug.append(node.slug)
        
        # delete old nodes
        for local_node in local_nodes_slug:
            # if local node not found in external nodes
            if not local_node in external_nodes_slug:
                # retrieve from DB and delete
                node = Node.objects.get(slug=local_node)
                node.delete()
                # then increment count that will be included in message
                deleted_nodes_count = deleted_nodes_count + 1
        
        # message that will be returned
        self.message = """
            %s nodes added
            %s nodes changed
            %s nodes deleted
            %s nodes unmodified
            
            %s total external records processed
            %s total local nodes for this layer
        """ % (
            len(added_nodes),
            len(changed_nodes),
            deleted_nodes_count,
            len(unmodified_nodes),
            len(items),
            Node.objects.filter(layer=self.layer).count()
        )