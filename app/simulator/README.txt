#-----------------------------------------------------#
# sender_simulator.sh                                 #
# receiver_simulator.sh                               #
#                                                     #
# Sender/receiver simulator for Tearing IF.           #
# Written by Akihiro Miyata on 2018/02/26.            #
# Copyright (c) 2018 Miyata Lab. All rights reserved. #
#-----------------------------------------------------#

What's this?
- Simulates sender/receiver behaviors using the command line.

How to use
- Step1: Run the server (python3 main.py).
- Step2: Place receipt jpg files in "./[sender, receiver]_receipt" directory.
- Step3: Modify "URL" in data_generator.sh if necessary.
- Step4: Run the script (sh [sender, receiver]_simulator.sh).

Notice
- All the receipts are related with default.jpg.
- "FILE_NAME: fail" indicates that there was a problem with the server side.
