#include <stdio.h>
#include <signal.h>
#include <unistd.h>

int main(void)
{
    if (setuid(0) < 0)
    {
        perror("setuid");
        return 1;
    }

    char flag[256] = {0};
    FILE *fp = fopen("/flag", "r");
    if (!fp)
    {
        perror("fopen");
        return 1;
    }

    fread(flag, sizeof(char), sizeof(flag), fp);
    printf("%s\n", flag);
    fclose(fp);

    int pid = fork();
    if (pid < 0)
    {
        perror("fork");
        return 1;
    }

    if (pid == 0)
    {
        sleep(10);
        kill(-1, SIGKILL);
        return 0;
    }

    return 0;
}