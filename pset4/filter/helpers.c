#include "helpers.h"
#include <math.h>

void swap(RGBTRIPLE *left, RGBTRIPLE *right);

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            float sum = 0;
            int average = 0;
            sum = image[i][j].rgbtRed + image[i][j].rgbtGreen + image[i][j].rgbtBlue;
            average = round(sum / 3);
            image[i][j].rgbtRed = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtBlue = average;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    int middle = width / 2;

    for (int i = 0; i < height; i++)
    {
        int lakan = 1;
        for (int j = 0; j < middle; j++)
        {
            swap(&image[i][j], &image[i][width - lakan]);
            lakan++;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp[height][width];
    float sumRed, sumGreen, sumBlue;
    int avgRed, avgGreen, avgBlue;

    //credits to amritamaz blog
    //check => http://amritamaz.net/blog/understanding-box-blur <= for better understanding

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            sumRed = 0, sumGreen = 0, sumBlue = 0;
            avgRed = 0, avgGreen = 0, avgBlue = 0;
            int divisor = 0;

            //this is the array of the location of all the boxes needed to be computed
            int row[] = { i - 1, i, i + 1 };
            int col[] = { j - 1, j, j + 1 };

            for (int r = 0; r < 3; r++)
            {
                for (int c = 0; c < 3; c++)
                {
                    int xpos = row[r];
                    int ypos = col[c];

                    if ((xpos >= 0 && xpos < height) && (ypos >= 0 && ypos < width))
                    {
                        //adding the original image value to the above variables
                        sumRed += image[xpos][ypos].rgbtRed;
                        sumGreen += image[xpos][ypos].rgbtGreen;
                        sumBlue += image[xpos][ypos].rgbtBlue;
                        divisor++;
                    }
                }
            }

            avgRed = round(sumRed / divisor);
            avgGreen = round(sumGreen / divisor);
            avgBlue = round(sumBlue / divisor);

            //setting the temp value
            temp[i][j].rgbtRed = avgRed;
            temp[i][j].rgbtGreen = avgGreen;
            temp[i][j].rgbtBlue = avgBlue;
        }
    }

    //change the original image value based on temp value
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = temp[i][j];
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp[height][width];

    //the 3x3 grid used to compute the x axis
    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};

    //the 3x3 grid used to compute the y axis
    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            float xsumRed = 0, xsumGreen = 0, xsumBlue = 0;
            float ysumRed = 0, ysumGreen = 0, ysumBlue = 0;
            int rtRed, rtGreen, rtBlue;

            //this is the array of the location of all the boxes needed to be computed
            int row[] = { i - 1, i, i + 1 };
            int col[] = { j - 1, j, j + 1 };

            for (int r = 0; r < 3; r++)
            {
                for (int c = 0; c < 3; c++)
                {
                    int xpos = row[r];
                    int ypos = col[c];

                    if ((xpos >= 0 && xpos < height) && (ypos >= 0 && ypos < width))
                    {
                        //the main computation of the image values based on cs50 walkthrough
                        xsumRed += Gx[r][c] * image[xpos][ypos].rgbtRed;
                        xsumGreen += Gx[r][c] * image[xpos][ypos].rgbtGreen;
                        xsumBlue += Gx[r][c] * image[xpos][ypos].rgbtBlue;

                        ysumRed += Gy[r][c] * image[xpos][ypos].rgbtRed;
                        ysumGreen += Gy[r][c] * image[xpos][ypos].rgbtGreen;
                        ysumBlue += Gy[r][c] * image[xpos][ypos].rgbtBlue;
                    }
                }
            }

            rtRed = round(sqrt((xsumRed * xsumRed) + (ysumRed * ysumRed)));
            rtGreen = round(sqrt((xsumGreen * xsumGreen) + (ysumGreen * ysumGreen)));
            rtBlue = round(sqrt((xsumBlue * xsumBlue) + (ysumBlue * ysumBlue)));

            //applying the computed value to the temp value
            temp[i][j].rgbtRed = rtRed > 255 ? 255 : rtRed;
            temp[i][j].rgbtGreen = rtGreen > 255 ? 255 : rtGreen;
            temp[i][j].rgbtBlue = rtBlue > 255 ? 255 : rtBlue;
        }
    }

    //change the original image value based on temp value
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = temp[i][j];
        }
    }

    return;
}

void swap(RGBTRIPLE *left, RGBTRIPLE *right)
{
    RGBTRIPLE mid = *left;
    *left = *right;
    *right = mid;
}
