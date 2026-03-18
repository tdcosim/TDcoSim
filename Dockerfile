FROM ubuntu:24.04
RUN apt update && apt -y upgrade
RUN DEBIAN_FRONTEND="noninteractive" apt install -y octave

# python deps
RUN apt install -y python3 python3-pip python3-virtualenv zip wget git
RUN mkdir ~/venv && cd ~/venv && virtualenv tdcosim

# matpower
RUN cd /home && wget -O matpower.zip https://github.com/MATPOWER/matpower/archive/refs/tags/8.0.zip && unzip matpower.zip && cd matpower-8.0

# tdcosim
RUN cd /home && git clone -b costadmg --depth 2 --single-branch https://github.com/tdcosim/TDcoSim.git
RUN /bin/bash -c 'source ~/venv/tdcosim/bin/activate && cd /home/TDcoSim/ && python3 -m pip install -e .'
RUN fpath="/home/TDcoSim/tdcosim/config/user_preference.json" && old=$(grep -i 'matpowerInstallLocation' $fpath) && new='"matpowerInstallLocation":"\/home\/matpower-8.0"' && sed -i "s/$old/$new/g" "$fpath"
ENTRYPOINT ["/bin/bash", "-c","source ~/venv/tdcosim/bin/activate && python3 /home/TDcoSim/tdcosim/server/main.py"]
