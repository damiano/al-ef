# Active Learning for Entity Filtering in Microblog Streams
Code and resources to reprude experiments decribed in SIGIR'15 short paper by Damiano Spina, Maria-Hendrike Peetz and Maarten de Rijke.
##Abstract

Monitoring the reputation of entities such as companies or brands in microblog streams (e.g., Twitter) starts by selecting mentions that are related to the entity of interest. Entities are often ambiguous (e.g., "Jaguar" or "Ford") and effective methods for selectively removing non-relevant mentions often use background knowledge obtained from domain experts. Manual annotations by experts, however, are costly. We therefore approach the problem of entity filtering with active learning, thereby reducing the annotation load for experts. To this end, we use a strong passive baseline and analyze different sampling methods for selecting samples for annotation. We find that margin sampling--an informative type of sampling that considers the distance to the hyperplane used for class separation--can effectively be used for entity filtering and can significantly reduce the cost of annotating initial training data.

##Citation
D. Spina, M.H. Peetz, M. de Rijke  
*Active Learning for Entity Filtering in Microblog Streams*  
Proceedings of 38th ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR). 2015.  

### BibTex
<pre>
@InProceedings{spina2015active,
authors={Spina, Damiano and Peetz, Maria-Hendrike and de Rijke, Maarten},
title={Active Learning for Entity Filtering in Microblog Streams},
booktitle={SIGIR '15: 38th international ACM SIGIR Conference on Research and Development in Information Retrieval},
year={2015},
organization={ACM} 
}
</pre>
