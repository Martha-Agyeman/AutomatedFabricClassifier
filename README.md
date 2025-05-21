Automated Fabric Detection System with Blockchain Integration
==========================================================

GitHub Repository: https://github.com/Martha-Agyeman/AutomatedFabricClassifier 

This system automatically detects fabric types and clothing items using computer vision and machine learning, providing sustainability recommendations and care instructions, with blockchain-based record keeping using Ganache.

System Requirements:
- Python 3.8+
- MySQL 8.0+
- Ganache (local blockchain emulator)
- Truffle Suite (for smart contract deployment)
- Web3.py (for Python blockchain integration)
- Arduino Uno with compatible sketch
- Device Webcam
- Node.js (16+) and npm

Installation:
1. Clone the repository
2. Install Python dependencies: pip install -r code/src/requirements.txt
3. Set up MySQL database using resources/database_schema.sql
4. Install and configure Ganache:
   - Download from https://trufflesuite.com/ganache/
   - Launch and create a new workspace
   - Note the RPC server address (usually http://127.0.0.1:7545)
5. Configure Arduino and connect to specified port
6. Update configuration in app.py and truffle-config.js as needed

Running the System:
1. Start Ganache
2. Deploy smart contracts: truffle migrate --network ganache
3. Start the Flask server: python code/src/app.py
4. Access the web interface at http://localhost:5001

Project Report Abstract:
The global fashion industry, one of the world's largest polluters, generates significant environmental and social challenges, 
particularly in Ghana, the largest market for second-hand apparel. This project explores the integration of Artificial Intelligence 
(AI), Blockchain, and Internet of Things (IoT) technologies to enhance sustainability in the Ghanaian fashion industry by addressing 
inefficiencies in textile waste management and supply chain transparency. The proposed system automates clothing categorization through 
an IoT-enabled image capture system and an AI-driven classification module, identifying fabric types, garment conditions, and recycling 
or upcycling potential. Blockchain technology ensures secure, immutable records of clothing data, promoting accountability and circular fashion practices.
Testing revealed high accuracy in AI classification and stakeholder satisfaction with automation, though challenges such as blockchain 
integration complexity and processing delays were noted. Recommendations include refining AI models, optimizing blockchain APIs, 
and enhancing user interfaces for broader adoption. The project demonstrates the feasibility of leveraging digital technologies to reduce 
textile waste, improve supply chain transparency, and foster sustainable practices in Ghana's fashion industry, offering a scalable model 
for similar contexts. Future work may explore lightweight blockchain alternatives and expanded AI capabilities for greater efficiency and impact. 



For detailed instructions, see docs/setup_guide.md
For user manual, see docs/manual.md
