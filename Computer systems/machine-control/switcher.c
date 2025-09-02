#include<stdio.h>

int main(int argc, char *argv[])
{

  	// Variable that select operation to perform
  	// i.e. switch variable


  	// Take input
    int a;
    char choice;
    // scanf(" %c", &choice);
    choice=*argv[1];
    // switch case with operation for each operator
    switch (choice) {
    case 'A':
        a=1;
        break;

    // case '-':
    //     printf("2");
    //     break;

    // case '*':
    //     printf("3");
    //     break;
    // case '/':
    //     printf("4");
    //     break;
    default:
        a=0;
    }
  
    return a;
    
}




