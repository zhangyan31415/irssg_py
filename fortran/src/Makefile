.SUFFIXES: .o .f .f90
F90 = ifort
FLAGS = -g -traceback -fpp #-DTEST
LDFLAGS  = $(FLAGS) -qmkl

ifndef ROOTDIR 
ROOTDIR=../
endif

REALMAKEFILE=Makefile.2

LIBS = -L$(ROOTDIR)/lib_ssg -lIRSSG

MODULES = comms.o init.o get_ssg.o comprel.o linear_rep.o
WAVEMD  = wave_data.o
VECT    = main.o 

ALL = $(MODULES) $(WAVEMD) $(VECT)

default:vasp

vasp:$(ALL)
	$(F90) $(LDFLAGS) -o irssg $(ALL) $(LIBS)
	# rm -r *.mod *.o


$(MODULES):%.o:%.f90
	$(F90) -c $(FLAGS) $*.f90
$(WAVEMD):%.o:%.f90
	ifort -g -traceback -assume byterecl -c $*.f90 
$(VECT):%.o:%.f90
	$(F90) -c $(FLAGS) $*.f90

clean:
	rm -r *.mod *.o irssg
