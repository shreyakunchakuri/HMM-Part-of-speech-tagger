
import sys

class hmmsmooth:

    def __init__(self,transition_map,emission_map,given_list):
        self.transition_map = transition_map
        self.emission_map = emission_map
        self.sentlist = given_list
        self.sing_tt = {}
        self.sing_tw = {}
        self.cts = {}
        self.cws = {}
        self.tags = {}
        
    def generate_STW(self):
        for word1 in self.emission_map.keys():
            count = 0
            for word2 in self.emission_map[word1].keys():
                if self.emission_map[word1][word2] == 1:
                    count = count + 1
            self.sing_tw[word1] = count

    def generate_STT(self):
        for word1 in self.transition_map.keys():
            count = 0
            for word2 in self.transition_map[word1].keys():
                if self.transition_map[word1][word2] == 1:
                    count = count + 1
            self.sing_tt[word1] = count


    def back_Off(self):
        for sentence in self.sentlist:
            tokens = sentence.split()
            for i in range(len(tokens)):
                word = tokens[i].rsplit('/',1)[0]
                tag = tokens[i].rsplit('/',1)[1]
                if tag in self.cts:
                    self.cts[tag] += 1
                else:
                    self.cts[tag] = 1
                if word in self.cws:
                    self.cws[word] += 1
                else:
                    self.cws[word] = 1
                if word in self.tags:
                    self.tags[word][tag] = 1
                else:
                    self.tags[word] = {}
                    self.tags[word][tag] = 1
        self.cts['END'] = len(self.sentlist)


class hmm:

    def __init__(self,given_list):

        self.list = given_list
        self.transition_map = {}
        self.emission_map = {}

    def training(self):
        for token in given_list:
            tokens = token.split()
            for i in range(len(tokens)-1):
                given_word = tokens[i].rsplit('/',1)[0]
                ctag = tokens[i].rsplit('/',1)[1]
                ntag = tokens[i+1].rsplit('/',1)[1]

                if i == 0:
                    if 'START' in self.transition_map:
                        if ctag in self.transition_map['START']:
                            self.transition_map['START'][ctag] += 1
                        else:
                           self.transition_map['START'][ctag] = 1
                    else:
                        self.transition_map['START'] = {}
                        self.transition_map['START'][ctag] = 1

                if ctag in self.transition_map:
                    if ntag in self.transition_map[ctag]:
                        self.transition_map[ctag][ntag] += 1
                    else:
                        self.transition_map[ctag][ntag] = 1
                else:
                    self.transition_map[ctag] = {}
                    self.transition_map[ctag][ntag] = 1

                if ctag in self.emission_map:
                    if given_word in self.emission_map[ctag]:
                        self.emission_map[ctag][given_word] += 1
                    else:
                        self.emission_map[ctag][given_word] = 1
                else:
                    self.emission_map[ctag] = {}
                    self.emission_map[ctag][given_word] = 1

                if i == len(tokens)-2:
                    end_word = tokens[i+1].rsplit('/',1)[0]
                    end_tag = ntag

                    if end_tag in self.transition_map:
                        if 'END' in self.transition_map[end_tag]:
                            self.transition_map[end_tag]['END'] += 1
                        else:
                            self.transition_map[end_tag]['END'] = 1
                    else:
                        self.transition_map[end_tag] = {}
                        self.transition_map[end_tag]['END'] = 1

                    if end_tag in self.emission_map:
                        if end_word in self.emission_map[end_tag]:
                            self.emission_map[end_tag][end_word] += 1
                        else:
                            self.emission_map[end_tag][end_word] = 1
                    else:
                        self.emission_map[end_tag] = {}
                        self.emission_map[end_tag][end_word] = 1


given_list = []
input_file = sys.argv[1]#"C:\\Users\\Shreya Kunchakuri\\Desktop\\CSCI 544\\HW5\\hmm-training-data\\it_isdt_train_tagged.txt"
with open(input_file,encoding='utf-8') as inp:
   for line in inp:
       given_list.append(line)
#print(len(given_list))
pos_tagger = hmm(given_list)
pos_tagger.training()
pos_t_smooth = hmmsmooth(pos_tagger.transition_map,pos_tagger.emission_map,given_list)
pos_t_smooth.generate_STT()
pos_t_smooth.generate_STW()
pos_t_smooth.back_Off()

for word1,val1 in pos_tagger.transition_map.items():
     count = 0
     for word2,val2 in val1.items():
         count = count + val2
     for word2,val2 in val1.items():
         val1[word2] = str(str(val2) + "/" + str(count))

for word1,val1 in pos_tagger.emission_map.items():
     count = 0
     for word2,val2 in val1.items():
         count = count + val2
     for word2,val2 in val1.items():
         val1[word2] = str(str(val2) + "/" + str(count))

mf = "../work/hmmmodel.txt"
with open(mf, 'w', encoding='utf-8') as out:
    out.write(str(pos_tagger.transition_map))
    out.write("\n")
    out.write(str(pos_tagger.emission_map))
    out.write("\n")
    out.write(str(pos_t_smooth.sing_tt))
    out.write("\n")
    out.write(str(pos_t_smooth.sing_tw))
    out.write("\n")
    out.write(str(pos_t_smooth.cts))
    out.write("\n")
    out.write(str(pos_t_smooth.cws))
    out.write("\n")
    out.write(str(pos_t_smooth.tags))
out.close()
