
import sys
import math


class hmm_model:
      def __init__(self,model_file):
        self.model_file = model_file
        self.transition_map = {}
        self.emission_map = {}
        self.sing_tt = {}
        self.sing_tw = {}
        self.cts = {}
        self.cws = {}
        self.ptt = {}
        self.ptw = {}
        self.n = 0
        self.V = 0
        self.pbaoffw = 0


      def smoothing(self,type,key1,key2,num,denom):
          lda = 1
          if type == 'T':
              if key1 in self.sing_tt:
                  lda += self.sing_tt[key1]
              val = float(float(num) + lda*self.ptt[key2])/float(float(denom) + lda)

          elif type == 'E':
              if key1 in self.sing_tw:
                  lda += self.sing_tw[key1]
              val = float(float(num) + lda*self.ptw[key2])/float(float(denom) + lda)

          elif type == 'MW':
              if key1 in self.sing_tw:
                  lda += self.sing_tw[key1]
              val = float(float(num) + lda * self.pbaoffw)/float(float(denom) + lda)

          elif type == 'MT':
              if key1 in self.sing_tt:
                  lda += self.sing_tt[key1]
              val = float(float(num) + lda * self.ptt[key2])/float(float(denom) + lda)

          return (val)
      
      def get_Model(self):
          with open(self.model_file, 'r', encoding="utf-8") as input:
              list_maps = input.read().split("\n")
              self.transition_map = eval(list_maps[0])
              self.emission_map = eval(list_maps[1])
              self.sing_tt = eval(list_maps[2])
              self.sing_tw = eval(list_maps[3])
              self.cts = eval(list_maps[4])
              self.cws = eval(list_maps[5])
              self.tag_Dict = eval(list_maps[6])

          for v in self.cws.values():
            self.n += v
          self.V = len(self.cws.keys())

          for t in self.cts.keys():
              self.ptt[t] = float(self.cts[t])/float(self.n)
          for w in self.cws.keys():
              self.ptw[w] = float(self.cws[w] + 1)/float(self.n + self.V)


          for key1 in self.transition_map.keys():
              for key2 in self.transition_map[key1].keys():
                  n,d = self.transition_map[key1][key2].split('/')
                  self.transition_map[key1][key2] = (float(n)/float(d))

          for key1 in self.emission_map.keys():
              for key2 in self.emission_map[key1].keys():
                  n,d = self.emission_map[key1][key2].split('/')
                  self.emission_map[key1][key2] = (float(n)+1/float(d))

          self.pbaoffw = float(1)/float(self.n + self.V)



class POS_Decoder:

     def __init__(self,sent,model_data):
        self.sent = sent
        self.transition_map = model_data.transition_map
        self.emission_map = model_data.emission_map
        self.viterbi_model = {}
        self.bp = {}
        self.otagL = []
        self.itagL = []
        self.tags = []
        self.pos_tag = ''
        self.model_data = model_data


     def decode(self):
         tokens = self.sent.split()
         if tokens[0] in model_data.tag_Dict:
             self.otagL = model_data.tag_Dict[tokens[0]].keys()
         else:
             self.otagL = list(self.transition_map.keys())
             self.otagL.remove('START')
         for k in self.otagL:
             if k in self.transition_map['START']:
                 self.viterbi_model[k] = {}
                 self.bp[k] = {}
                 if tokens[0] in self.emission_map[k]:
                     self.viterbi_model[k][0] = self.transition_map['START'][k] * self.emission_map[k][tokens[0]]
                 else:
                     self.viterbi_model[k][0] = self.transition_map['START'][k] * model_data.smoothing('MW',k,tokens[0],0,model_data.cts[k])

                 self.bp[k] = {}
                 self.bp[k][0] = 'START'

         for i in range(1,len(tokens)):
             if tokens[i] in model_data.tag_Dict:
                 self.otagL = model_data.tag_Dict[tokens[i]].keys()
             else:
                 self.otagL = list(self.transition_map.keys())
                 self.otagL.remove('START')
             for key1 in self.otagL:

                 maxV = 0
                 if tokens[i-1] in model_data.tag_Dict:
                     self.itagL = model_data.tag_Dict[tokens[i-1]].keys()
                 else:
                     self.itagL = list(self.transition_map.keys())
                     self.itagL.remove('START')
                 for key2 in self.itagL:
                     if key1 in self.transition_map[key2]:
                        if tokens[i] in self.emission_map[key1] and key2 in self.viterbi_model and i-1 in self.viterbi_model[key2]:
                           maxV = max(maxV,self.viterbi_model[key2][i-1]*self.transition_map[key2][key1]*self.emission_map[key1][tokens[i]])
                        elif key2 in self.viterbi_model and i-1 in self.viterbi_model[key2]:
                           maxV = max(maxV,self.viterbi_model[key2][i-1] * self.transition_map[key2][key1] * model_data.smoothing('MW',key1,tokens[i],0,model_data.cts[key1]))

                     else:
                         if tokens[i] in self.emission_map[key1] and key2 in self.viterbi_model and i-1 in self.viterbi_model[key2]:
                           maxV = max(maxV,self.viterbi_model[key2][i-1]*model_data.smoothing('MT',key2,key1,0,model_data.cts[key2])*self.emission_map[key1][tokens[i]])
                         elif key2 in self.viterbi_model and i-1 in self.viterbi_model[key2]:
                           maxV = max(maxV,self.viterbi_model[key2][i-1] * model_data.smoothing('MT',key2,key1,0,model_data.cts[key2]) * model_data.smoothing('MW',key1,tokens[i],0,model_data.cts[key1]))


                 if key1 in self.viterbi_model:
                   self.viterbi_model[key1][i] = maxV
                 else:
                   self.viterbi_model[key1] = {}
                   self.viterbi_model[key1][i] = maxV


                 maxV = 0
                 argM = ''
                 for key2 in self.itagL:
                    if key1 in self.transition_map[key2]:
                        if key2 in self.viterbi_model and i-1 in self.viterbi_model[key2]:
                           curr_val = self.viterbi_model[key2][i-1]*self.transition_map[key2][key1]
                           if maxV <= curr_val:
                              maxV = curr_val
                              argM = key2
                    else:
                        if key2 in self.viterbi_model and i-1 in self.viterbi_model[key2]:
                           curr_val = self.viterbi_model[key2][i-1]*model_data.smoothing('MT',key2,key1,0,model_data.cts[key2])
                           if maxV <= curr_val:
                              maxV = curr_val
                              argM = key2


                 if key1 in self.bp:
                    self.bp[key1][i] = argM
                 else:
                    self.bp[key1] = {}
                    self.bp[key1][i] = argM


         maxV = 0
         argM = ''
         if tokens[len(tokens)-1] in model_data.tag_Dict:
             self.otagL = model_data.tag_Dict[tokens[len(tokens)-1]].keys()
         else:
             self.otagL = list(self.transition_map.keys())
             self.otagL.remove('START')
         for key1 in self.otagL:
             if 'END' in self.transition_map[key1]:
                 curr_val = self.viterbi_model[key1][len(tokens)-1]*self.transition_map[key1]['END']
                 if maxV <= curr_val:
                      maxV = curr_val
                      argM = key1
             else:
                 curr_val = self.viterbi_model[key1][len(tokens)-1]*model_data.smoothing('MT',key1,'END',0,model_data.cts[key1])
                 if maxV <= curr_val:
                      maxV = curr_val
                      argM = key1


         self.viterbi_model['END'] = {}
         self.bp['END'] = {}
         self.viterbi_model['END'][len(tokens)-1] = maxV
         self.bp['END'][len(tokens)-1] = argM


     def backtrack(self):
         tokens = self.sent.split()
         tag = (self.bp['END'][len(tokens)-1])
         self.tags.append(tag)

         prevTag = tag
         for i in range(len(tokens)-1, -1, -1):
            currTag = self.bp[prevTag][i]
            self.tags.append(currTag)
            prevTag = currTag

         self.tags.reverse()

     def POS_Tag(self):

         tokens = self.sent.split()
         for i in range(len(tokens)):
             self.pos_tag = self.pos_tag + tokens[i] + '/' + self.tags[i+1] + ' '



model_file = "../work/hmmmodel.txt"
model_data = hmm_model(model_file)
model_data.get_Model()

answer = []

with open(sys.argv[1], 'r', encoding="utf-8") as inp:
    for line in inp:
        decode = POS_Decoder(line,model_data)
        decode.decode()
        decode.backtrack()
        decode.POS_Tag()
        answer.append(decode.pos_tag)

with open('hmmoutput.txt','w', encoding="utf-8") as out:
    for r in answer:
        out.write(r + "\n")
out.close()
