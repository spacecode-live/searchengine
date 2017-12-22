#include <cmath>
#include <iostream>
#include <fstream>
#include <set>
#include <string>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
#include <iomanip>

using namespace std;

bool keepRunning = true;
double dValue;
unordered_set<int> pagesVirtualConn;
unordered_map<int, vector<int>> pagesToPage;
unordered_map<int, int> pageToPagesSize;
unordered_map<int, double> values;

bool openFile(string vertexSum, string vertexInput, string edgeInput) {
	ifstream vertexSumReader(vertexSum);
	ifstream vertexFileReader(vertexInput);
	ifstream edgeFileReader(edgeInput);
	string oneLine;
	int amountOfNodes = 0;
	double initValue;
	if(vertexSumReader.is_open() && getline(vertexSumReader, oneLine)) {
		stringstream tmpOneLine(oneLine);
		string title;
		tmpOneLine >> title >> amountOfNodes;
		initValue = 1.0 / amountOfNodes;
		vertexSumReader.close();
	}
	else {
		cerr << "cannot open file for reading " << vertexSum << endl;
		return false;
	}
	if(vertexFileReader.is_open()) {
		while(getline(vertexFileReader, oneLine)) {
			stringstream tmpOneLine(oneLine);
			int id;
			string label;
			tmpOneLine >> id >> label;
			values[id] = initValue;
			pageToPagesSize[id] = 0;
		}
		vertexFileReader.close();
	}
	else {
		cerr << "cannot open file for reading " << vertexInput << endl;
		return false;
	}
	if(edgeFileReader.is_open()) {
		while(getline(edgeFileReader, oneLine)) {
			stringstream tmpOneLine(oneLine);
			int id1, id2;
			tmpOneLine >> id1 >> id2;
			if(id1 != id2) {
				if(pagesToPage.find(id2) == pagesToPage.end()) {
					vector<int> newVecvtor;
					newVecvtor.push_back(id1);
					pagesToPage[id2] = newVecvtor;
				}
				else {
					pagesToPage[id2].push_back(id1);
				}
					++pageToPagesSize[id1];
			}
		}
		edgeFileReader.close();
	}
	else {
		cerr << "cannot open file for reading " << edgeInput << endl;
		return false;
	}
	return true;
}

bool writeFile(string fileName) {
	ofstream fileWriter(fileName);
	double total = 0;
	if(fileWriter.is_open()) {
		for(auto it = values.begin(); it != values.end(); ++it) {
			fileWriter << it->first << "," <<setprecision(4)<<scientific<< it->second << "\n";
			total += it->second;
		}
		fileWriter.close();
		cout << "total = " << total << endl;
	}
	else {
		cerr << "cannot open file for writing " << fileName << endl;
		return false;
	}
	return true;
}

void oneRound(double &nopr, double d, bool converge = false, double convergeLimit = 0) {
	cout << "enter oneRound function" << endl;
	unordered_map<int, double> newValues;
	double oneMinusDN = (1 - d) / values.size();
	int convergeCount = 0;
	int count = 1;
	for(auto idx = values.begin(); idx != values.end(); ++idx) {
		double value = 0;
		// find all pages point to current page
		vector<int>* pagesToCurrentPage = &pagesToPage[idx->first];
		for(auto jdx = pagesToCurrentPage->begin(); jdx < pagesToCurrentPage->end(); ++jdx) {
			int pageId = *jdx;
			value += values[pageId]/pageToPagesSize[pageId];
		}
		if(pagesVirtualConn.find(idx->first) != pagesVirtualConn.end()) {
			value += (nopr - idx->second) / (values.size() - 1);
		}
		else { // not no outlink page
			value += nopr/(values.size() - 1);
		}
		newValues[idx->first] = value * d + oneMinusDN;
		// check converge
		if(converge && abs(newValues[idx->first] - idx->second) / idx->second < convergeLimit) {
			convergeCount++;
		}
		count++;
	}
	values.swap(newValues);
	nopr = 0; 
	for(auto it = pagesVirtualConn.begin(); it != pagesVirtualConn.end(); ++it) {
		nopr += values[*it];
	}
	if(converge && values.size() == convergeCount) {
		keepRunning = false;
	}
}

int main(int argc, char *argv[]) {
	if(argc < 8) {
		cerr << "Too less arguments" << endl;
		exit(1);
	}
	// open file and get data
	double cValue = -1.0;
	int kValue = -1;
	dValue = atof(argv[1]);
	string argument2(argv[2]);
	if(argument2 == "-k"){
		kValue = atoi(argv[3]);
	}
	else { // get cValue
		cValue = atof(argv[3]);
	}
	string vertexSum(argv[4]),
		   vertexFile(argv[5]),
		   edgeFile(argv[6]),  
		   outputFile(argv[7]);

	if(openFile(vertexSum, vertexFile, edgeFile)) {
		cout << "reading data from file done" << endl;
		// find pages with no outlink
		double sumOfNoOutPageRank = 0;
		for(auto it = pageToPagesSize.begin(); it != pageToPagesSize.end(); ++it) {
			if(it->second == 0) {
				pagesVirtualConn.insert(it->first);
				sumOfNoOutPageRank += values[it->first];
			}
		}
		cout << "find all pages with no outlink" << endl;
		// run page rank
		if(kValue >= 0) {
			for(int idx = 0; idx < kValue; ++idx) {
				oneRound(sumOfNoOutPageRank, dValue);
			}
		}
		else { // cValue > 0
			do {
				oneRound(sumOfNoOutPageRank, dValue, true, cValue);
			} while(keepRunning);
		}
		// write output into file
		writeFile(outputFile);
	}
	return 0;
}