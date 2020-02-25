import numpy as np
from keras.models import Sequential
from keras.layers import Dense,Activation

class GeneticAlgorithm:
	def __init__(self):
		self.genomes=0

	def mutation(self,wlist,mean,deviation):
		mutated_list=[]
		for fw in wlist:
			r=np.random.rand(1,len(fw)).astype(float)
			m=r*2*deviation+mean-deviation
			l=np.add(fw,m).astype(float)
			mutated_list.append(l[0])
		return mutated_list

	def mutatemodel(self,weight,mean,deviation,nos):
		mutated_list=[]
		mutated_list.append(weight)
		for i in range(nos-1):
			r=np.random.rand(1,len(weight)).astype(float)
			m=r*2*deviation+mean-deviation
			l=np.add(weight,m).astype(float)
			mutated_list.append(l[0])
		return mutated_list

	def crossover(self,fwlist):
		crossovered_list=[]
		lenght=len(fwlist)
		for i in range(lenght-1):
			for j in range(lenght):
				d1,d2=fwlist[i],fwlist[j]
				l=len(d1)
				pos=np.random.randint(0,l,1)[0]
				end_pos=pos+np.random.randint(0,l,1)[0]
				end_pos=l if end_pos >l else end_pos
				
				temp=d2[pos:end_pos].copy()
				d2[pos:end_pos],d1[pos:end_pos]=d1[pos:end_pos],temp

				crossovered_list.append(d1)
				crossovered_list.append(d2)
		return crossovered_list

	def sort_network(self,network_list,nos):
		network_list.sort(key=lambda x:x.fitness,reverse=True)
		new_list=sorted(network_list,key=lambda x:x.fitness,reverse=True)
		#print("from sort",new_list[0].fitness,new_list[9].fitness)
		return new_list[0:nos]

	def show(self):
		print("from inside")

	def call(self):
		self.show()
		show()

	def applyGenetic(self,fp,best_gene,nos):
		##sorted_network=self.sort_network(network_list)
		##parent=sorted_network[0:8]
		##parent.extend(sorted_network[-3:-1])
		##fp=[flatten_weights(m1.model.get_weigths()) for m1 in parent]
		co_offsprings=self.crossover(fp)
		mutated_offsprings=self.mutation(fp,0,0.5)
		no_offspring=len(mutated_offsprings)
		selected_crossover=co_offsprings[0:nos-no_offspring-1]
		new_genes=[]
		new_genes.append(best_gene)
		new_genes.extend(mutated_offsprings)
		new_genes.extend(selected_crossover)
		


		#uf_genes=[unflatten_weights(network_list[0].model.get_weigths(),new_gene) for new_gene in new_genes]
		return new_genes ##new genes and present best gene



def flatten_weights(weights):
	x=[]
	for weight in weights:
		x=np.append(x,weight.flatten())
	return x

def unflatten_weights(weights,fw):
	n_w=[]
	index=0
	for x in range(len(weights)):
		i =weights[x].shape
		if len(i)==1:
			a=fw[index:index+i[0]]
			index+=i[0]
			n_w.append(a)
		elif len(i)==2:
			nos=i[0]*i[1]
			b=fw[index:index+nos]
			index+=nos
			a=np.reshape(b,(i[0],i[1]))
			n_w.append(a)
	return n_w

def show():
	print("hello")
	

