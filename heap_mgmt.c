
#include <stdio.h>
#include <stdlib.h>

#define BUFF_SIZE 1000

typedef struct Node Node;
struct Node{
  char *string;
  struct Node* next;
};

Node* ROOT = NULL;

Node* create_node(void){
  Node *node = (Node*)malloc(sizeof(Node));
  if(node==NULL){
    printf("malloc error\n");
    exit(0);
  } else {
    node->next = NULL;
    return node;
  }
}

void free_all(Node *node){
  if(node->next != NULL){
    free_all(node->next);
  }
  free(node->string);
  free(node);
}

void print_values(Node *node){
  while(1){
    printf("value: %s\n",node->string);
    if(node->next!=NULL){
      node = node->next;
    } else {
      break;
    }
  }
}

void append_node(Node *new_node, Node *node){
    while(node->next != NULL){
      node = node->next;
    }
    node->next = new_node;
}

int get_string_length(char buffer[]){
  int i;
  for(i=0;buffer[i]!='\0';i++){};
  return i;
}

char* create_string(char buffer[]){
  int i;
  int length = get_string_length(buffer);
  char* str = (char*)malloc(length+1);
  for(i=0;i<length;i++){
    str[i] = buffer[i];
  }
  str[length] = '\0';
  return str;
}

void init_heap(void){
  ROOT = create_node();
  ROOT->string = NULL;
  ROOT->next = NULL;
}

void cleanup_heap(void){
  free_all(ROOT);
}

void getstring(char **output){
  Node *new_node;
  char buffer[BUFF_SIZE];
  scanf("%s",buffer);
  new_node = create_node();
  new_node->string = create_string(buffer);
  append_node(new_node, ROOT);
  *output = new_node->string;
}

int main(void){
  char *ptr;

  init_heap();
/*
  printf("Enter string:");
  getstring(&ptr);
  printf("string: %s\n",ptr);

  printf("Enter string:");
  getstring(&ptr);
  printf("string: %s\n",ptr);

  printf("Enter string:");
  getstring(&ptr);
  printf("string: %s\n",ptr);
*/
  print_values(ROOT);
  cleanup_heap();
  return 0;
}
