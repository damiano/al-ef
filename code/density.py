#!/usr/bin/env python
import numpy

def jaccquard_similarity(a, b):
    if len(b) == 0 or len(a) == 0: return 0.0
    return len(set(a).intersection(b))*1./len(set(a).union(set(b)))

def similarityMatrix(features):
  a = numpy.zeros((len(features), len(features)),
                     dtype=numpy.float)
  ids = list(features.keys())
  id2row = {}
  for i, idi in enumerate(ids):
    id2row[idi] = i
    for j, idj in enumerate(ids):
      if i == j:
         a[i, j] = 1
         break
      a[i, j] = jaccquard_similarity(features[idi][0].keys(),
                                     features[idj][0].keys())
      a[j, i] = a[i, j]
  return a, id2row

def density(matrix, row):
   return numpy.mean(matrix[row,:])

def k_density(matrix, row, k=5):
   r = matrix[row,:]
   return numpy.mean(numpy.sort(r[1:k+1])[::-1])

def margin_density(distance, matrix, row):
   return (1-density(matrix, row)*(1-distance))

def margin_k_density(distance, matrix, row, k=5):
   return (1-k_density(matrix, row, k)*(1-distance))

def main():
  pass

if __name__ == '__main__':
  main()
