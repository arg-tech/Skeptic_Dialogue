import json
import datetime
from app.textParser import TextParser


class SkepticDialogue:
    
    """
    This method takes as input a nodeID and returns the complete node/object
    from the aif json object.
    """
    def find_aif_node(self, aif, nodeID):
        for row in aif['nodes']:
            if(row['nodeID'] == nodeID):
                return row
        
    """
    This method takes as input an I-node and returns the connected L-node
    """
    def get_Lnode(self, aif, inodeID):
        #get the edges that result to the iNodeID
        edges_targetting_I = [edge for edge in aif['edges'] if edge['toID'] == inodeID]
        
        for e in edges_targetting_I:
            s_nodeID = e['fromID']
            s_node = self.find_aif_node(aif, s_nodeID)
            # find the incoming YAs
            if(s_node['type'] == "YA"):
                yaID  = s_node['nodeID']
                edges_targetting_YA = [edge for edge in aif['edges'] if edge['toID'] == yaID]
                lnodeID = edges_targetting_YA[0]['fromID']
                lnode = self.find_aif_node(aif, lnodeID)
                return lnode

    """
    This method takes as input an AIF node and returns the related L-nodes. 
    """
    def getRelatedLocutions(self, aif, node):
        locutions = []
        
        #If the node is an S-node, we identify the incoming/outgoing I-nodes and then move to their connecting locutions.
        if node['type'] == "RA" or node['type'] == "CA" or node['type'] == "MA" or node['type'] == "TA" or node['type'] == "PA":
            nodeID = node['nodeID']

            for edge in aif['edges']:
                if edge['fromID'] == nodeID: #search for outgoing edges
                    toID = edge['toID']
                    nodeTo = self.find_aif_node(aif, toID)
                    if nodeTo['type'] == "I":
                        loc = self.get_Lnode(aif, nodeTo['nodeID'])
                        locutions.append(loc)
                
                elif edge['toID'] == nodeID: #search for incoming edges
                    fromID = edge['fromID']
                    nodeFrom = self.find_aif_node(aif, fromID)
                    if nodeFrom['type'] == "I":
                        loc = self.get_Lnode(aif, nodeFrom['nodeID'])
                        locutions.append(loc)
                        
        # if the node is an I-node, we get directly the connected locution.             
        elif node['type'] == "I":
            loc = self.get_Lnode(aif, node['nodeID'])
            locutions.append(loc)
            
        return locutions




    """
    This method returns the most recent locution from an array of locutions, based 
    on the way they are arranged in the ordered_locutions array.
    """
    def most_recent_locution(self, locutions, ordered_locutions):
        latest_loc = None
        i_latest = 0
        for loc in locutions:
            if loc != None:
                for i in range(len(ordered_locutions)):
                    if loc['nodeID'] == ordered_locutions[i] and i > i_latest:
                        i_latest = i
                           
        return ordered_locutions[i_latest]


    """
    This method parses the HTML tags in the original text and extracts the list of 
    of locution ids, ordered according to the sequence appeared in the text.
    """
    def order_locutions_from_text(self, original_text):
        locutions = []
        textparser = TextParser()
        textparser.feed(original_text)

        # Extract data from parser
        tags  = textparser.NEWTAGS #parse html tags
        attrs = textparser.NEWATTRS # parse attributes
        data  = textparser.HTMLDATA  #parse html data
        # Clean the parser
        textparser.clean()
        
        for i in range(len(attrs)):
            if len(attrs[i]) > 0: 
              
                for j in range(len(attrs[i])):
                    if(attrs[i][j][0] == 'id'):
                        #the att[i][j] contains the "node" attribute of the <span> tag. The "node" prefix is then removed
                        locutions.append(attrs[i][j][1].replace("node", "")) 
      
        return locutions


    def has_prompt(self, loc_ID, prompts):
        loc_prompts = []
        for prom in prompts:
            if loc_ID == prom[0]:
                loc_prompts.append((prom[1], prom[2]))
        return loc_prompts


    def print_dialogue(self, ordered_locutions, prompts, aif):
        text = ""
        
        for locID in ordered_locutions:
            loc_node = self.find_aif_node(aif, locID)
            text = text + "- " + loc_node['text'] + '\n'
            loc_prompts = self.has_prompt(locID, prompts)
            for lp in loc_prompts:
                if(lp[1] == 'proposition'):
                    prompt = "   [AVAILABLE MOVE] DEBIASING AGENT: " + lp[0]
                    text = text + prompt + "\n"
                elif(lp[1] == 'structure'):
                    prompt = "   [AVAILABLE MOVE] BIAS AGENT: " + lp[0]
                    text = text + prompt + "\n"
                elif(lp[1] == 'scheme'):
                    prompt = "   [AVAILABLE MOVE] CRITIC AGENT: " + lp[0]
                    text = text + prompt + "\n"
        return text
        
    """
    This method takes as input a filename that points to a Json file which is the result of 
    the Skeptic service and returns an array of tuples, where each tuple contains the nodeID of
    the locution after which there must be a prompt from the agent, and the text of that prompt.

    """
    def generate_dialogue(self, data):
        prompts = []
        
        #create separate JSON objects for the Skeptic, AIF and original_text object.
        skeptic = data["Skeptic"]
        aif = data["AIF"]
        original_text = data["text"]

        ordered_locutions = self.order_locutions_from_text(original_text)
        #iterate through the "questions" part of the initial json output.  
        for row in skeptic['questions']:
            nodeID = row['nodeID']
            aif_node = self.find_aif_node(aif, nodeID);
            #for each of the node id existing in the question json object, find the related locutions
            
            locutions = self.getRelatedLocutions(aif, aif_node)
                     
            #from these locutions find the most recent one.
            latest_locution = self.most_recent_locution(locutions, ordered_locutions)
            if latest_locution != None:
                #add a tuple of the latest locution ID and the prompt to be given.
                prompt_tuple = (latest_locution, row['question'], row['type'])
                prompts.append(prompt_tuple)
            
            
        dialogue = self.print_dialogue(ordered_locutions, prompts, aif)

        return dialogue

        
        
        
