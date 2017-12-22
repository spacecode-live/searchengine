#ifndef readFiles_H
#define readFiles_H

#include <fstream>
#include <iostream>
#include <sstream>
#include <cctype>
#include <algorithm>
#include <string>
#include <vector>
#include <unordered_map>

using namespace std;

void readNet(string inputFileName, unordered_map<int, string> &netNodes, unordered_map<int, vector<int>* > &netPointing, unordered_map<int, vector<int>* > &netPointed){
	ifstream netFile(inputFileName);
	if (netFile.is_open()) {
		string line;
        getline(netFile, line);
        stringstream ssv(line);
        string tmp;
        ssv >> tmp;
        if (tmp == "*Vertices"){
            int amount;
            ssv >> amount;
            for (int i = 0; i < amount; i++) {
                getline(netFile, line);
                stringstream ssrv(line);
                int nodeId;
                string nodeLabel;
                ssrv >> nodeId >> nodeLabel;
                netNodes[nodeId] = nodeLabel;
            }
        }
        getline(netFile, line);
        stringstream sse(line);
        sse >> tmp;
        if (tmp == "*Arcs") {
            int amount;
            sse >> amount;
            for (int i = 0; i < amount; i++) {
                getline(netFile, line);
                stringstream ssre(line);
                int startId;
                int endId;
                ssre >> startId >> endId;
                if (startId != endId){
                    if (! netPointing.count(startId)) {
                        vector<int> *endIdsetPtr = new vector<int>;
                        netPointing[startId] = endIdsetPtr;
                    }
                    netPointing[startId]->push_back(endId);
                    if (! netPointed.count(endId)) {
                        vector<int> *startIdsetPtr = new vector<int>;
                        netPointed[endId] = startIdsetPtr;
                    }
                    netPointed[endId]->push_back(startId);
                }
            }
        }
		netFile.close();
	}
}

void readInvindex(string inputFileName, unordered_map<string, vector<int>* > &invIndex){
	ifstream indexFile(inputFileName);
	if (indexFile.is_open()){
		string line;
		while (getline(indexFile, line)){
			stringstream ss(line);
			string word;
			int pageId;
			ss >> word;
			transform(word.begin(), word.end(), word.begin(), ::tolower);
			ss >> pageId;
			if (!invIndex.count(word)){
				vector<int> *pageIdsetPtr = new vector<int>;
				invIndex[word] = pageIdsetPtr;
			}
			invIndex[word]->push_back(pageId);
		}
		indexFile.close();
	}
}

#endif