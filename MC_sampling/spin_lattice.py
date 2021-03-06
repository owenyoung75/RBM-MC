import math
import random
import operator as op_external
import numpy as np
# import tensorflow as tf


mag = 0.5


class Spin(object):
    def __init__(self,
                 magnitude = mag,
                 state = None
                 ):
    	dic = {}
#         dic[None] = None
    	for i in range(int(mag*2+1)):
    		dic[i] = i - mag
    	self.mag = magnitude
    	self.dic = dic
    	self.state = state
    	if state == None:
    		self.randomize()
    	self.value = self.dic[self.state]    	
    	
    def flip(self):
        self.state = 1 - self.state
        
    def randomize(self):
    	self.state = random.randint(0, len(self.dic)-1)
    	
    def copy(self):
    	s = Spin(state = self.state)
    	return s
    	
    def vector(self):
    	vec = np.zeros(int(mag*2+1))
    	vec[self.state] = 1
    	return vec
#    	vec = tf.constant(vec)




class lattice(object):
	def __init__(self,
                 dim = 1,
                 size = 4,
                 config = None
                 ):
		self.dim = dim
		self.size = size
		if config:
			self.config = config
		else:
			self.initialization()
			
	def initialization(self):
		if self.dim == 1:
			fig_1 = []
			for _ in range(self.size):
				fig_1.append(Spin())
			self.config = fig_1
		else:
			fig_d = []
			for _ in range(self.size):
				fig_d.append(lattice(dim=(self.dim-1),
									 size=self.size
									).config)
			self.config = fig_d
                
	def get_output(self):
		result = self.config
		for _ in range(self.dim - 1):
			result = sum(result, [])
		return ([spin.state for spin in result],
                [spin.value for spin in result])
    	
	def nearby(self, pos):  
		nears = []
		for i in range(self.dim):
			left = list(pos)
			right= list(pos)
			left[i] -= 1
			right[i]+= 1
			if left[i] < 0:
				left[i] = self.size - 1
			if right[i] == self.size:
				right[i] = 0
			nears.append(left)
			nears.append(right)
		return nears 
    	
	def get_random_position(self):       # position vector pos[x,y,z]
		pos = []
		for _ in range(self.dim):
			pos.append(random.randint(0, self.size - 1))
		return pos
    	
	def get_spin_by_lattice_position(self, pos):  # spin at site = pos
		getter = self.config
		for i in range(self.dim):
			getter = getter[pos[i]]
		return getter
    	    	
	def all_sites(self):
		res = []
		def traverse(pos):
			for x in range(self.size):
				pos.append(x)
				if len(pos) == self.dim:
					res.append(list(pos))
				else:
					traverse(pos)
				pos.pop()
		traverse([])
		return res
    	
	def magnetization(self):
		m = 0 
		position = self.all_sites()
		for pos in position:
			m += self.get_spin_by_lattice_position(pos).value()
		return m
		
	def __eq__(self, other):
		if self.get_output() == other.get_output():
			return True
		else:
			return False        



class State(object):	
	def __init__(self, dic):
		self.dic = dic
        	self.components = dic.keys()       # components are lattice objects
        	self.coefficients = dic.values()
        	self.normalize()
        	self.n_spins = (dic.keys()[0].size) ** (dic.keys()[0].dim)
		
	def str(self):
		output = ''		
		for cpt in self.components:
			if self.dic[cpt] :
				if self.dic[cpt] == 1:
					string = '|'
				else:
					string = str(self.dic[cpt]) + '|'
				states, values = cpt.get_output()
				for value in values:
					string += str(value) + ', '
				string += '>' + ' +'
				output += string
			
        	output = output[:-1]
        	return output

	def normalize(self):
		z = np.sqrt( sum(np.square(np.abs(self.coefficients))) )
		self.coefficients = np.multiply(self.coefficients, (1/z))
		return self
			
	def __add__(self, other):
		if not self.n_spins == other.n_spins:
			raise TypeError("two states must contain same number of spins")
		states = self
		for cpt in other.components:
			if cpt in states.dic.keys():
				states.dic[cpt] += other.dic[cpt]
			else:
				states.dic[cpt]  = other.dic[cpt]
		states.normalize()
		states.components = states.dic.keys()
		states.coefficitents = states.dic.values()
		return states
		
	def __radd__(self, other):
		if other == 0:
			return self
		else:
			return self.__add__(other)
			
	def __mul__(self, other):
		prod = 0.0
		for cpt in self.components:
			if cpt in other.dic.keys():
				prod += self.dic[cpt] * other.dic[cpt]
		return prod
		
	def __rmul__(self, other):
		self.coefficients = np.multiply(self.coefficients, other)
		return self.normalize()
		
	def single_spin_operation(self, site, matrix):
		dic = {}
        	for cpt in self.components:
            		spin = cpt.get_spin_by_lattice_position(site)
            		spin_vector = spin.vector()
            		spin_vector = matrix.dot(spin_vector)
            		site_dic = {}     		
            		for i in range(spin_vector.shape[0]):
                		if spin_vector[i]:
                    			site_dic[i] = spin_vector[i]	# non-zero elements
            		for i in site_dic.keys():
                		fig = list(cpt.config)
                		fig[site[0]] = Spin(state = i)		# only for 1D case
                		lat = lattice(dim = cpt.dim, size = cpt.size, config = fig)
                		coef = site_dic[i] * self.dic[cpt]
                		dic[lat] = coef                  
		rlt = State(dic = dic)
		return rlt

	def operated(self, operator):
		rlt = 0
		print
        	for pos in operator.positions:
            		state = self
            		st, vl = state.components[0].get_output()
            		print(st)
            		matrices = operator.dic[str(pos)]
            		for i in range(len(pos)):
                		site = pos[i]
                		matrix = matrices[i]
                		print(matrix, site)
                		state = state.single_spin_operation(site = site, matrix = matrix)
                	st, vl = state.components[0].get_output()
                	print(st)
            		rlt += state
            		print
        	return rlt





class operator(object):
# 	operator has attributes:
# 		spin magnitude
# 		positions-groups
# 		symbols-groups
# 		matrices-groups
# 		dic = { str(positions) : matrices }
# 	Note:
# 		positions and matrices need to be updated by hand if any change, since not functions
	def __init__(self, spin = mag, positions = None, symbols = None):
		self.spin = spin
        	self.symbols = symbols
        
        	if symbols == None:
            		self.dic = None
            		self.matrices = None
            		self.positions = None
        	else:
            		matrices = []
            		i = -1
            		for symbol in self.symbols:
                		i = i+1
                		matrices.append([])   # list object for each term
                		for sbl in symbol:
                    			matrices[i].append(SpinMatrices(spin, sbl)) # list of arrays on each site
            		self.dic = {}
            		for i in range(len(positions)):
                		positions[i] = sorted(positions[i])     # element in positions is made of position-coordinates, we sort them
                		self.dic[str(positions[i])] = matrices[i]
            		self.matrices = self.dic.values()
            		self.positions = sorted(positions)          # Eventually we sort the terms
            		
             		
# #     	def str(self):
# #     		output = ''
# #     		for i in range(len(self.positions)):
# #     			output += '('
# #     			position = self.positions[i]
# #     			symbol = self.symbols[i]
# #     			for j in range(len(position)):
# #     				output += '[' + symbol[j] + ',' + str(position[j]) +']' + '*'
# #     			output = output[:-1]
# #     			output += ')' + '+'
# #     		output = output[:-1]
# #     		return output
 

	def __add__(self, other):
		rlt = operator(spin = self.spin, positions = None, symbols = None) # When add terms, we don't care about symbols
        	positions = list(other.positions)
        	dic = dict(other.dic)
        	rlt.dic = self.dic
        	rlt.dic.update(dic)
        	dic_additive = {}
        	for pos in self.positions:
            		if pos in other.positions:
                		dic_additive[str(pos)] = list( np.asarray(self.dic[str(pos)]) + np.asarray(other.dic[str(pos)]) )
            		else:
                		positions.append(pos) # creat the positions list for rlt
        	rlt.dic.update(dic_additive)
        	rlt.positions = sorted(positions)
        	return rlt

	def __radd__(self, other):
		if other == 0:
			return self
		else:
			return self.__add__(other)

	def __sub__(self, other):
		rlt = operator(spin = self.spin, positions = None, symbols = None) # When subtract terms, we don't care about symbols
        	positions = list(other.positions)
		
        	dic = dict(other.dic)
        	for value in dic.values():
            		for site_matrix in value:
                		site_matrix = - site_matrix
        	rlt.dic = self.dic.update(dic)
        
        	dic_additive = {}
        	for pos in self.positions:
            		if pos in other.positions:
                		sites_matrices = np.asarray(self.dic[str(pos)]) - np.asarray(other.dic[str(pos)])
                		dic_additive[str(pos)] = []
                		for site_matrix in sites_matrices:
                    			dic_additive[str(pos)].append(site_matrix) # add terms acting on the same site
            		else:
                		positions.append(pos) # creat the positions list for rlt
        	rlt.dic = rlt.dic.update(dic_additive)
        	rlt.positions = sorted(rlt.positions)
        	return rlt


	def __mul__(self, other):
		if type(other) == int:
			return other * self
		rlt = operator(spin = self.spin, positions = None, symbols = None) # When multiply terms, we don't care about symbols
        	rlt.positions = []
        	rlt.dic = {}
        	for pos_a in self.positions:
            		for pos_b in other.positions:

                		pos = list(pos_a)
                		mat = list(self.dic[str(pos_a)])
                		mat_extra = list(other.dic[str(pos_b)])
                
                		for site in pos_b:
                    			if site in pos:
                        			mat[pos.index(site)] = mat[pos.index(site)].dot( mat_extra[pos_b.index(site)] )
                    			else:
                        			pos.append(site)
                        			mat.append(mat_extra[pos_b.index(site)])
                
                		posr = sorted(pos)
                		mats = []
                		for site in posr:
                			mats.append(mat[pos.index(site)])
                			
                		rlt.positions.append(posr)
                		if str(posr) in rlt.dic.keys():
                    			rlt.dic[str(posr)] = list( np.asarray(rlt.dic[str(posr)]) + np.asarray(mats) )
                		else:
                    			rlt.dic[str(posr)] = mats
        	rlt.positions = sorted(rlt.positions)
        	return rlt

	def __rmul__(self, other):
		for cpt in self.dic.keys():
			self.dic[cpt][0] *= other
		return self




def SpinMatrices(spin, powered_symbol):
    if powered_symbol == []:
        return np.asarray([])   
    if type(powered_symbol) == str:
    	symbol = powered_symbol
    	power = 1
    else:
    	symbol= powered_symbol[0]
    	power = powered_symbol[1]
    
    dim = int(spin*2+1)
    mat = np.zeros([dim,dim])
    
    if (symbol == 'z') or (symbol == 'sz') or (symbol == 3):
        sz = spin
        for i in range(dim):
            mat[i,i] = sz
            sz = sz - 1

    if (symbol == '+') or (symbol == 's+'):
        for i in range(dim-1):
            mat[i,i+1] = 1.0

    if (symbol == '-') or (symbol == 's-'):
        for i in range(dim-1):
            mat[i+1,i] = 1.0

    if (symbol == 'x') or (symbol == 'sx') or (symbol == 1):
        for i in range(dim-1):
            mat[i,i+1] = 0.5
            mat[i+1,i] = 0.5

    if (symbol == 'y') or (symbol == 'sy') or (symbol == 2):
        for i in range(dim-1):
            mat[i,i+1] =  0.5
            mat[i+1,i] = -0.5
        mat = mat * (-1j)

    mat = mat**power
    return mat

    
