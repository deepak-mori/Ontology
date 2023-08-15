import os
import rdflib
import xml.etree.ElementTree as ET
from rdflib.namespace import FOAF, XSD
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import  RDF, RDFS

myNamespace = "http://www.semanticweb.org/rogstrix/ontologies/2023/3/ecommerce1"
namedIndividual = URIRef('http://www.w3.org/2002/07/owl#NamedIndividual')
rdftype = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

def make_graph(inputs):
    for i in graphs.subjects():
        if(inputs in str(i)):
            return True
    return False

cwd = os.getcwd()
formed_tree = ET.parse('ecommerce1.xml')

# Traversing over the root of the tree to fetch the required data.

tree_root = formed_tree.getroot()
customers ={}
products = {}
reviews = {}

for root_child in tree_root:

    if root_child.tag == "products":

        for children in root_child:
            id = int(children.find('id').text)
            products[id] = {}
            products[id]['price']  = children.find('price').text
            products[id]['name'] = children.find('name').text
            products[id]['availability']  = children.find('availability').text
            products[id]['description']  = children.find('description').text
            products[id]['rating']  = children.find('rating').text
            products[id]['brand']  = children.find('brand').text
            
    if root_child.tag == "customers":

        for children in root_child:
            id = int(children.find('id').text)
            customers[id] = {}
            customers[id]['email']  = children.find('email').text
            customers[id]['name'] = children.find('name').text
            customers[id]['phone']  = children.find('phone').text
    
    if root_child.tag == "reviews":

        for children in root_child:
            id = int(children.find('id').text)
            reviews[id] = {}
            reviews[id]['customer_id']  = children.find('customer_id').text
            reviews[id]['review_text']  = children.find('review_text').text
            reviews[id]['product_id'] = children.find('product_id').text
            reviews[id]['rating']  = children.find('rating').text
            reviews[id]['date']  = children.find('date').text              

# Call to make the graph
graphs = Graph()
graphs.parse("ecommerce1.owl", format = 'xml')
print("OWL file is loaded")

RDFTriplesFromed = []
proIDTocnt = {}

for j in customers.keys():
    PName = str(myNamespace) + "#" + ("_".join(str(customers[j]["name"]).split(' ')))
    individual_a = URIRef(PName)
    aclass = str(myNamespace) + "#" + "customer"
    
    if(make_graph(PName) == False): 
        RDFTriplesFromed.append((individual_a, RDF.type, URIRef(aclass)))
        RDFTriplesFromed.append((individual_a, RDF.type, URIRef(namedIndividual)))

        # Adding Data Property - id, name, phone number of the customer.
        sub = individual_a

        pred = URIRef(str(myNamespace) + "#id")
        literals = customers[j]['id']
        RDFTriplesFromed.append((sub, pred, Literal(literals, datatype = XSD.string)))

        pred = URIRef(str(myNamespace) + "#name")
        literals = customers[j]['name']
        RDFTriplesFromed.append((sub, RDFS.label, Literal(literals, datatype = XSD.string)))

        pred = URIRef(str(myNamespace) + "#phone")
        literals = customers[j]['phone']
        RDFTriplesFromed.append((sub, pred, Literal(literals, datatype = XSD.string)))

for i in products.keys():
    proIDTocnt[i] = str(products[i]["name"])
    PName = str(myNamespace)+ "#" + str(products[i]["name"])
    individual_a = URIRef(PName)
    aclass = str(myNamespace)+ "#" + "product"
    if(make_graph(PName) == False): 
        RDFTriplesFromed.append((individual_a, RDF.type, URIRef(aclass)))
        RDFTriplesFromed.append((individual_a, RDF.type, URIRef(namedIndividual)))
        pred = URIRef(str(myNamespace) + "#product")
        sub = URIRef(PName)  
        literals = i
        RDFTriplesFromed.append((sub, pred, Literal(literals, datatype = XSD.string)))

for i in RDFTriplesFromed:
    graphs.add(i)

print("The new RDF Triples formed - ")

for i in RDFTriplesFromed:
    print(i[0])
    print(i[1])
    print(i[2])
    print("--------------")

print("Number of new RDF Triples formed- ", len(RDFTriplesFromed))
graphs.serialize(destination = "ecommerce1_final.owl", format = 'xml')

# Checking consitency and inferences

from owlready2 import *
from rdflib.compare import to_isomorphic, graph_diff

ontology = get_ontology(cwd + "/ecommerce1.owl").load()

#Checking consistency for approach 1
with ontology:
    sync_reasoner()
ontology.save("ecommerce1_consistent.owl")

graph2 = rdflib.Graph()
graph2.parse("ecommerce1_final.owl", format = 'xml')

index = 0
for s,p,o in graph2:
    index = index + 1
    
print("No of Triples Before : " ,index)

graph3 = rdflib.Graph()
graph3.parse("ecommerce1_consistent.owl", format='xml')

index = 0
for s,p,o in graph3:
    index = index + 1

print("No of Triples After : " , index)

isomorph1 = to_isomorphic(graph2)
isomorph2 = to_isomorphic(graph3)

if(isomorph1 == isomorph2):
    print("No Inferences made. ")
else:
    both, fir, sec = graph_diff(isomorph1, isomorph2)
    print("New Inderences and All Inferences Generated...")
    def n_sorting(g, f):
        for p in sorted(g.serialize(format='nt').splitlines()):
            if(p) : 
                f.write(p)
                f.write("\n") 

    fil = open("newInferences.txt", "w")
    n_sorting(sec, fil)
    fil.close()

    fil = open("AllExtractedInferences.txt", "w")
    n_sorting(both, fil)
    n_sorting(sec, fil)
    fil.close()

    