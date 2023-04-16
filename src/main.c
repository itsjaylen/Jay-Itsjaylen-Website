#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <pthread.h>
#include <postgresql/libpq-fe.h>

#define _CRT_SECURE_NO_WARNINGS // To disable deprecation warnings on Visual Studio
#define MAX_LINE_LEN 1024

struct arg_struct {
    const char* filename;
    const char** usernames;
    int num_usernames;
    const char* date_str;
    const char* name_str;
};





// Function to connect to the database
PGconn* connect_to_database(const char* db_url) {
    // Create a connection object using the given connection string
    PGconn *conn = PQconnectdb(db_url);
    // Check if the connection was successful
    if (PQstatus(conn) != CONNECTION_OK) {
        // If the connection failed, print an error message and return NULL
        fprintf(stderr, "Connection to database failed: %s", PQerrorMessage(conn));
        PQfinish(conn);
        return NULL;
    }
    // If the connection was successful, return the connection object
    return conn;
}

// Function to insert a message into the database
int insert_message(PGconn* conn, const char* timestamp, const char* channel, const char* username, const char* message) {
    // Construct the SQL INSERT statement with placeholders for the variables
    const char *insert_stmt = "INSERT INTO twitchmessages (timestamp, channel, username, message) "
                              "VALUES ($1, $2, $3, $4)";

    // Create an array of the variable values
    const char *values[4] = { timestamp, channel, username, message };

    // Create a parameter array with the length of the variable values array
    const int param_lengths[4] = { strlen(timestamp), strlen(channel), strlen(username), strlen(message) };
    const int param_formats[4] = { 0, 0, 0, 0 };

    // Execute the SQL statement with the variable values
    PGresult *res = PQexecParams(conn, insert_stmt, 4, NULL, values, param_lengths, param_formats, 0);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        // If the query failed, print an error message and return 1
        fprintf(stderr, "Query failed: %s", PQerrorMessage(conn));
        PQclear(res);
        return 1;
    }

    PQclear(res);
    // If the query was successful, return 0
    return 0;
}



int insert_messages_from_csv(PGconn* conn, const char* filename) {
    printf("Inserting messages from file %s\n", filename);

    // Open the CSV file for reading
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error opening file %s\n", filename);
        return 1;
    }

    // Read each line from the file and insert it into the database
    char line[1084];
    long int line_start_pos = 0;
    while (fgets(line, 1084, file)) {
        // Check if the line exceeds the maximum length
        if (strlen(line) > 500) {
            printf("Skipping line that exceeds maximum length of 500 characters\n");
            continue;
        }

        // Remove the trailing newline character from the line
        line[strcspn(line, "\n")] = 0;

        // Remove invisible characters from the line
        for (int i = 0; i < strlen(line); i++) {
            if (isspace(line[i]) && line[i] != ' ') {
                line[i] = ' '; // Replace invisible character with space character
            }
        }

        // Split the line into fields using the semicolon delimiter
        char *timestamp, *username, *date, *channel, *message;
        timestamp = strtok(line, ";");
        username = strtok(NULL, ";");
        date = strtok(NULL, ";");
        channel = strtok(NULL, ";");
        message = strtok(NULL, ";");

        // Combine the date and timestamp into one variable
        char datetime[50];
        snprintf(datetime, 50, "%s %s", date, timestamp);

        // Call the insert_message function to insert the message into the database
        int result = insert_message(conn, datetime, channel, username, message);
        if (result != 0) {
            fprintf(stderr, "Error inserting message: %s %s %s %s\n", datetime, channel, username, message);
        }

        // Store the current file position
        line_start_pos = ftell(file);
    }

    // Close the file
    fclose(file);

    // Truncate the file to remove the lines that have already been read
    FILE *file_trunc = fopen(filename, "w");
    fseek(file_trunc, line_start_pos, SEEK_SET);
    fclose(file_trunc);

    printf("Messages inserted from file %s\n", filename);
    return 0;
}







void remove_bad_unicode(char* str) {
    unsigned char* p = (unsigned char*)str;
    while (*p) {
        if (*p > 0x7f) {
            *p = '?'; // Replace bad Unicode with a question mark
        }
        p++;
    }
}

void process_file(const char* filename, const char** usernames_to_print, int num_usernames_to_print, const char* date_str, const char* name_str) {
    char line[102400];
    FILE* fp = fopen(filename, "r");
    if (fp == NULL) {
        fprintf(stderr, "Error opening file %s.\n", filename);
        return;
    }

    // Open file for appending
    FILE* out_fp = fopen("output.csv", "a");
    if (out_fp == NULL) {
        fprintf(stderr, "Error opening output file.\n");
        return;
    }

    while (fgets(line, sizeof(line), fp)) {
        // Remove bad unicode
        remove_bad_unicode(line);

        // Remove extra spaces
        char* pos = line;
        while (*pos == ' ') {
            pos++;
        }
        char* new_pos = pos;
        int inside_space = 0;
        while (*pos) {
            if (*pos == ' ') {
                inside_space = 1;
            } else {
                if (inside_space) {
                    *new_pos++ = ' ';
                    inside_space = 0;
                }
                *new_pos++ = *pos;
            }
            pos++;
        }
        if (*(new_pos - 1) == ' ') {
            *(new_pos - 1) = '\0';
        } else {
            *new_pos = '\0';
        }

        // Extract timestamp
        char timestamp[9];
        if (sscanf(line, "[%8s]", timestamp) != 1) {
            //fprintf(stderr, "Error parsing file %s. Malformed line: %s\n", filename, line);
            continue;
        }

        // Extract username
        char* username_start = strchr(line, ' ') + 1;
        char* username_end = strchr(username_start, ':');
        if (username_end == NULL) {
            //fprintf(stderr, "Error parsing file %s. Malformed line: %s\n", filename, line);
            continue;
        }
        *username_end = '\0';
        char* username = username_start;

        // Check whether username should be printed
        int should_print = 0;
        for (int i = 0; i < num_usernames_to_print; i++) {
            if (strcmp(username, usernames_to_print[i]) == 0) {
                should_print = 1;
                break;
            }
        }
        if (!should_print) {
            continue;
        }

        // Extract message
        char* message_start = username_end + 2;

        // Write to file in CSV format
        //fprintf(out_fp, "%s;%s;%s;%s;%s\n", date_str, name_str, timestamp, username, message_start);
        fprintf(out_fp, "%s;%s;%s;%s;%s\n", timestamp, username, date_str, name_str, message_start);
    }

    fclose(fp);
    fclose(out_fp);
}





void* process_file_thread(void* arg) {
    struct arg_struct* args = (struct arg_struct*)arg;
    const char* filename = args->filename;
    const char** usernames = args->usernames;
    int num_usernames = args->num_usernames;
    const char* date_str = args->date_str; // Get date_str from arg_struct
    const char* name_str = args->name_str; // Get name_str from arg_struct

    process_file(filename, usernames, num_usernames, date_str, name_str); // Pass date_str to process_file()

    return NULL;
}


void process_directory(const char* dirname, const char** usernames, int num_usernames) {
    DIR* dir = opendir(dirname);
    if (dir == NULL) {
        fprintf(stderr, "Error opening directory %s.\n", dirname);
        return;
    }

    pthread_t threads[1024];
    int thread_count = 0;

    struct dirent* entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_DIR) {
            char path[1024];
            snprintf(path, sizeof(path), "%s/%s", dirname, entry->d_name);
            printf("%s\n", path); // Replace with return value
        } else if (entry->d_type == DT_REG && strstr(entry->d_name, ".log") != NULL) {
            char path[1024];
            snprintf(path, sizeof(path), "%s/%s", dirname, entry->d_name);
            int start_index = strstr(entry->d_name, "-") - entry->d_name + 1;
            int end_index = start_index + 10;
            char name_str[256];
            strncpy(name_str, entry->d_name, start_index);
            name_str[start_index - 1] = '\0';
            char date_str[256];
            strncpy(date_str, entry->d_name + start_index, 10);
            date_str[10] = '\0';
            printf("%s\n", date_str); // Replace with return value
            printf("%s\n", name_str); // Replace with return value

            // Call process_logs function with the directory path and date_str
process_file(path, usernames, num_usernames, date_str, name_str);

        }
    }

    closedir(dir);
}



typedef struct {
  char time[9]; // Format: "HH:MM:SS"
  char name[256];
  char message[500];
} Message;

int compare_messages(const void* a, const void* b) {
  const Message* ma = (const Message*) a;
  const Message* mb = (const Message*) b;
  return strcmp(ma->time, mb->time);
}

Message* csv_reader() {
  FILE *fp;
  char line[MAX_LINE_LEN];
  Message* messages = NULL;
  int num_messages = 0;
  int max_messages = 20000;
  
  fp = fopen("output.csv", "r");
  if (fp == NULL) {
    printf("Error opening file\n");
    exit(1);
  }
  
  messages = malloc(max_messages * sizeof(Message));
  
  while (fgets(line, MAX_LINE_LEN, fp)) {
    Message msg;
    sscanf(line, "%8[^,],%255[^,],%255[^\n]", msg.time, msg.name, msg.message);
    if (num_messages >= max_messages) {
      max_messages += 1000;
      messages = realloc(messages, max_messages * sizeof(Message));
    }
    messages[num_messages] = msg;
    num_messages++;
  }
  
  fclose(fp);
  
  qsort(messages, num_messages, sizeof(Message), compare_messages);
  
  return messages;
}





int main() {
    const char* usernames[] = {"icyjaylenn"};
    const int num_usernames = sizeof(usernames) / sizeof(char*);
    process_directory("./logs", usernames, num_usernames);

    return 0;
} 
