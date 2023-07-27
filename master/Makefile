CXX=g++
RM=rm -f

CPPFLAGS=-g0 -Wall
LDFLAGS= 
LIBDEPS=-lmosquitto -pthread

SRCS=ah_master.cpp TelegramInterface.cpp ThingSpeakUpdater.cpp autohome.cpp
OBJS=$(subst .cpp,.o,$(SRCS))

all: ah_master

ah_master: $(OBJS)
	$(CXX) $(LDFLAGS) -o ah_master $(OBJS) $(LIBDEPS)

autohome: autohome.cpp
	$(CXX) $(CPPFLAGS) -c autohome.cpp

TelegramInterface: TelegramInterface.cpp
	$(CXX) $(CPPFLAGS) -c TelegramInterface.cpp

ThingSpeakUpdater: ThingSpeakUpdater.cpp
	$(CXX) $(CPPFLAGS) -c ThingSpeakUpdater.cpp

clean:
	$(RM) *.o

distclean: clean
	$(RM) ah_master *.log
