#include <cstdlib>
#include <iostream>
#include <string>
using namespace std;

int main(int argc, char *argv[]) {
    // Check for input errors
    if(argc != 2) {
        cout << "Usage: " << argv[0] << " <orion-filename>" << endl;
        exit(1);
    }
    // Read the input
    string fileName = argv[1];
    string command = "python3 main.py " + fileName;
    system(command);
    return 0;
}