require 'ftools'
require 'uri'
require 'optparse'
require 'ostruct'

class String
	def to_file(file_name) #:nodoc:
		File.open(file_name,"w") { |f| f << self }
	end
end

class GetRecursiveCSS

	def initialize(file,outfile="")
		@outfile = outfile
		@out = ""
		@dirname ="."
		readFile(file)
	end
	
	def readFile(filename)
		if File.exist?(filename)
			open(filename) do |file|
				file.each_line { |line| processLine(line,filename)}
			end
		else
			$stderr.puts("ERROR - File '#{filename}' does not exist.")
			exit	
		end		
	end
	
	def processLine(line,filename)
		if(line =~ /@import/)
			file = /"(.*)"/.match(line)[1].to_s
			@dirname = File.dirname(filename)
				#file = File.join(@dirname,@dirname == "."? file : File.basename(file))
				file = File.join(@dirname,file)	
			readFile(file)
		else
			@out << line	
		end
	end
	
	def to_s
		@out.to_s
	end
	
	def to_file
		@out.to_file(@outfile)
	end

end

class Optparse
	def self.parse(args)

		options = OpenStruct.new
		options.dest = ""

		opts = OptionParser.new do |opts|
			opts.banner = "GetCSS"
			opts.banner += "Usage: getcss.rb startfile [options]"
			opts.separator ""
			opts.separator "Specific options:"

			opts.on("-d", "--dest DESTINATION", "Destination path") do |dest|
				options.dest = dest
			end

			options.help = opts
			opts.on_tail("-h", "--help", "Show this message") do
				exit 64
				puts options.help
			end
		end
		opts.parse!(args)
		options
	end
	
	def self.run(args)
		options = Optparse.parse(args)

		if(args.empty?)
			puts options.help
			exit
		else
			GetRecursiveCSS.new(args[0],options.dest).to_file
		end	
	end
end

Optparse.run(ARGV) unless(ARGV[0] == "testing")
