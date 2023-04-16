import ctypes
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def main():
    # create an engine to connect to the database using the URL
    engine = create_engine(
        "postgresql://postgres:password@192.168.240.2:5432/flaskappmain"
    )

    # create a Session class bound to the engine
    Session = sessionmaker(bind=engine)

    # create a base class for declarative models
    Base = declarative_base()

    # define a model for the twitchusers table
    class TwitchUsers(Base):
        __tablename__ = "twitchusers"

        id = Column(Integer, primary_key=True)
        username = Column(String(50), nullable=False)
        message_count = Column(Integer, default=0, nullable=False)
        average_message_length = Column(Integer, default=0, nullable=False)
        role = Column(String(50), default="user", nullable=False)
        daily_average_message_count = Column(Integer, default=0, nullable=False)

    # create a session to interact with the database
    session = Session()

    # query the twitchusers table and print the rows
    usernames_list = session.query(TwitchUsers.username).all()
    usernames_list = [username[0] for username in usernames_list if username[0] != "icyjaylenn"]
    usernames_list = tuple(usernames_list)
    # usernames_list = ("zoidnl", "should", "haziqpng", "Hxrtwell_", "afroakatsuki", "rodorigesuuu")
    usernames_list = ["abysss_888"]

    session.close()
    # time.sleep(30)

    def clean(filename):
        print("Cleaning file", filename)
        lines = set()
        with open(filename, "r") as f:
            for line in f:
                # Remove leading/trailing whitespaces and newlines
                line = line.strip()
                # Skip empty lines
                if not line:
                    continue
                lines.add(line)

        with open(filename, "w") as f:
            f.write("\n".join(lines))

        print("Duplicate lines and empty newlines removed from file", filename)

    def insert_messages_from_csv(conn_str, filename):
        # Load the shared library
        lib = ctypes.cdll.LoadLibrary("./main.so")

        # Define the argument and return types of the function
        lib.insert_messages_from_csv.argtypes = [
            ctypes.c_void_p,  # PGconn* conn
            ctypes.c_char_p,  # const char* filename
        ]
        lib.insert_messages_from_csv.restype = ctypes.c_int

        # Open a connection to the PostgreSQL database
        conn = ctypes.c_void_p(lib.PQconnectdb(conn_str))

        # Call the C function with the appropriate arguments
        filename = filename.encode("utf-8")
        result = lib.insert_messages_from_csv(conn, filename)

        # Check the result and print an error message if necessary
        if result != 0:
            print("Error inserting messages from file")

    # Define the Message struct
    class Message(ctypes.Structure):
        _fields_ = [
            ("time", ctypes.c_char * 9),
            ("name", ctypes.c_char * 256),
            ("message", ctypes.c_char * 500),
        ]

    # Load the shared library
    lib = ctypes.CDLL("./main.so")

    # Define the argument types for process_directory
    lib.process_directory.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_char_p),
        ctypes.c_int,
    ]

    # Define the return type for process_directory
    lib.process_directory.restype = None

    # Set up the arguments
    dirname = b"./logs"
    # usernames_list = ("zoidnl",)

    usernames = (ctypes.c_char_p * len(usernames_list))(
        *[str.encode(username) for username in usernames_list]
    )
    num_usernames = ctypes.c_int(len(usernames_list))

    start_time = time.time()

    # Call process_directory
    lib.process_directory(dirname, usernames, num_usernames)

    lib.csv_reader.restype = ctypes.POINTER(Message)

    try:
        # Call the csv_reader function
        messages = lib.csv_reader()

        # Free the memory allocated by the C code
        lib.free(messages)
    except IndexError:
        print("IndexError")

    clean("./output.csv")
    insert_messages_from_csv(
        b"postgresql://postgres:password@192.168.240.2:5432/flaskappmain",
        "./output.csv",
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print("Elapsed time: {:.2f} seconds".format(elapsed_time))


if __name__ == "__main__":
    main()
