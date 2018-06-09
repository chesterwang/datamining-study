#coding:utf8
import gzip,struct,numpy as np
import matplotlib.pyplot as plt


def test_read_image(filename):
    """
    filename 是gzip格式文件
    """
    f = gzip.open(filename)
    buf = f.read()
    index = 0
    magic, numImages, numRows,numColumns = struct.unpack_from('>llll',buf,index)
    print magic, numImages, numRows,numColumns 
    index = struct.calcsize('>llll')

    im = struct.unpack_from('>784B' ,buf, index)
    index += struct.calcsize('>784B')
     
    im = np.array(im)
    im = im.reshape(numRows,numColumns)
    
    fig = plt.figure()
    plotwindow = fig.add_subplot(111)
    plt.imshow(im , cmap='gray')
    plt.show()
    


if __name__ == "__main__":
    #filename = "/home/chester/Downloads/train-labels-idx1-ubyte.gz"
    filename = "/home/chester/Downloads/train-images-idx3-ubyte.gz"
    test_read_image(filename)
