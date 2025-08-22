# Please run the following commands before make
# echo "export IRVSPDATA="`pwd` >> ~/.bashrc
# source ~/.bashrc

F90 = ifort
FLAGS = -fpp -g -traceback -check all 

REALMAKEFILE=Makefile.2 

default:lib

lib:
	$(MAKE) -f $(REALMAKEFILE) libs 

clean:
	rm -r *.mod *.o libIRVSP.a
